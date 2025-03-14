from dataclasses import dataclass, field
import os
import json
import time
from pydantic import BaseModel, Field
import requests
import csv
from csv_processor import CSVProcessor
from langchain.chat_models import init_chat_model
from langchain.chat_models.base import BaseChatModel
from typing import Dict, Any, Tuple, List
from langchain.schema import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
import urllib3

# 禁用不安全请求的警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class JudgeResult(BaseModel):
    """
    评估结果
    """

    result: str = Field(description="The result of the judge.Should be either '是' or '否'.")

@dataclass
class AgentEvaluator:
    """
    一个用于评估AI助手性能的类,通过测试用例文件进行评估。
    """
    
    case_file: str
    result_file: str
    llm_chain: Runnable = field(default=None)
    model: str = field(default="openai/gpt-4o-mini") 
    agent_api: str = field(default="https://dynamic14.eeo.im/ai-agent-lab/stream")
        
    def __post_init__(self):
        self.csv_reader = CSVProcessor(self.case_file)
        
        provider, model = self.model.split("/", maxsplit=1)
        
        if provider == "hunyuan":
            provider = "openai"
            url = "https://api.hunyuan.cloud.tencent.com/v1"
            key = os.getenv("HUNYUAN_API_KEY")
            llm = init_chat_model(model, model_provider=provider, temperature=0, base_url=url, api_key=key)
        else:
            llm = init_chat_model(model, model_provider=provider, temperature=0)
            
        llm = llm.with_structured_output(JudgeResult)
        
        prompt = ChatPromptTemplate.from_template("""
            我现在在开发一个agent，这个agent能够根据用户的问题给出回答。现在需要跑一个测试，用于评估这个agent的效果。
            下面我会给出这个agent在测试中的回答，同时为了评估其效果，也会给出标准答案。
            你需要做的就是帮我判断下这个agent的回答是否与标准答案相匹配。
            如果是，请输出"是"，否则输出"否"。
            
            注意：你的判断会影响到agent的评估结果，请谨慎判断。

            标准答案: {standard_answer}
            
            AI助手回答: {agent_answer}"""
        )
        
        self.llm_chain = prompt | llm
    
    def call_agent(self, payload: Dict[str, Any]) -> Tuple[str, int]:
        """
        调用agent接口并解析响应
        
        Args:
            payload: 请求参数，JSON格式
            
        Returns:
            Tuple[str, int]: 包含最后一个message的content内容和首个token响应的耗时（秒）
        """
        start_time:int = int(time.time())
        first_token_time:int = 0
        last_message_content:str = ""
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        # 使用stream=True来处理流式响应
        response = requests.post(
            self.agent_api,
            json=payload,
            headers=headers,
            stream=True,
            verify=False  # 禁用SSL证书验证
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"请求失败，状态码: {response.status_code}")
        
        # 处理流式响应
        for line in response.iter_lines():
            if not line:
                continue
                
            # 解析SSE格式的数据行
            if line.startswith(b'data: '):
                data_str = line.decode('utf-8')[6:]  # 去掉'data: '前缀
                try:
                    data = json.loads(data_str)
                    
                    # 检查是否是第一个token类型的响应
                    if data.get("type") == "token" and first_token_time == 0:
                        first_token_time = int(time.time()) - start_time
                    
                    # 保存最后一个message类型的响应内容
                    if data.get("type") == "message" and "content" in data:
                        message_content = data["content"].get("content", "")
                        if message_content:
                            last_message_content = message_content
                except json.JSONDecodeError:
                    continue
            
        return last_message_content, first_token_time
    
    def _write_row_to_csv(self, row: List[str], mode: str = 'a') -> None:
        """
        将一行数据写入CSV文件
        
        Args:
            row: 要写入的行数据
            mode: 文件打开模式，'w'表示覆盖写入，'a'表示追加写入
        """
        with open(self.result_file, mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    
    def evaluate_from_csv(self) -> None:
        """
        从CSV文件中读取测试用例，评估agent的回答并将结果写回CSV文件
        
        CSV文件格式要求：
        - index=1: 问题
        - index=3: 是否跳过（"否"表示跳过）
        - index=4: 标准答案
        - index=5: agent回答（将被写入）
        - index=6: 是否跳过（"否"表示跳过）
        - index=7: 首个token响应时间（将被写入）
        - index=8: 评估结果（将被写入）
        """
        
        # 读取所有行（包括标题行）
        all_rows = self.csv_reader.read_all_rows()
        if not all_rows or len(all_rows) <= 1:
            print("CSV文件为空或只有标题行\n")
            return
        
        # 获取标题行
        header = all_rows[0]
        
        # 先清理结果文件并写入标题行
        self._write_row_to_csv(header, mode='w')
        
        # 处理每一行数据
        for i in range(1, len(all_rows)):
            line_number:int = i + 1
            row = all_rows[i]
            
            # 确保行有足够的列
            while len(row) < 9:
                row.append("")
            
            # 检查是否需要跳过（当index=3或index=6列内容是"否"时跳过）
            if row[3] == "否" or row[6] == "否":
                print(f"跳过第{line_number}行（无效case）\n")
                self._write_row_to_csv(row)
                continue
            
            # 获取问题和标准答案
            question = row[1]
            standard_answer = row[4]
            
            if not question or not standard_answer:
                print(f"跳过第{line_number}行（问题或标准答案为空）\n")
                self._write_row_to_csv(row)
                continue
            
            print(f"处理第{line_number}行: {question}\n")
            
            # 调用 agent 并评估结果
            try:
                # 构建payload
                payload = {
                    "message": question,
                    "agent_config": {"class_id": 317973, "teacher_id": 100146}
                }
                
                # 调用 agent 并获取响应
                agent_answer, first_token_time = self.call_agent(payload)
                print(f"agent 回答(响应时间: {first_token_time}秒): \n{agent_answer}\n")
                
                # 将结果写入行
                row[5] = agent_answer
                row[7] = str(first_token_time)
            except Exception as e:
                print(f"调用 agent 失败: {str(e)}\n")
                row[5] = str(e)
                self._write_row_to_csv(row)
                continue
            
            # 使用LLM评估回答
            try:
                evaluation_result = self.llm_chain.invoke({"standard_answer": standard_answer, "agent_answer": agent_answer})
                print(f"LLM 评估结果: {evaluation_result.result}\n")
                
                if evaluation_result.result == "是":
                    row[8] = "是"
                else:
                    row[8] = "否"
            except Exception as e:
                print(f"调用 llm 失败: {str(e)}\n")
                row[8] = str(e)
                self._write_row_to_csv(row)
                continue
            
            # 立即将处理完的行写入结果文件
            self._write_row_to_csv(row)
            
            print(f"第{line_number}行处理完成并已写入文件\n")
        
        print("评估完成")

# evaluation = AgentEvaluator(case_file="teacher_case.csv", result_file="teacher_case_result.csv", model="hunyuan/hunyuan-turbos-20250226")
evaluation = AgentEvaluator(case_file="teacher_case.csv", result_file="teacher_case_result.csv", model="openai/gpt-4o-mini")
evaluation.evaluate_from_csv()