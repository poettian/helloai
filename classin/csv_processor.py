import csv
from typing import List, Dict, Iterator, Optional, Union
import os


class CSVProcessor:
    """
    CSV文件处理类，提供逐行读取CSV数据和计算行数的功能
    """
    
    def __init__(self, file_path: str, encoding: str = 'utf-8', delimiter: str = ','):
        """
        初始化CSV处理器
        
        Args:
            file_path: CSV文件路径
            encoding: 文件编码，默认为utf-8
            delimiter: CSV分隔符，默认为逗号
        """
        self.file_path = file_path
        self.encoding = encoding
        self.delimiter = delimiter
        
        # 验证文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 验证文件是否为CSV格式
        if not file_path.lower().endswith('.csv'):
            raise ValueError(f"文件不是CSV格式: {file_path}")
    
    def count_rows(self) -> int:
        """
        计算CSV文件的总行数（包括标题行）
        
        Returns:
            int: CSV文件的总行数
        """
        with open(self.file_path, 'r', encoding=self.encoding) as file:
            reader = csv.reader(file, delimiter=self.delimiter)
            row_count = sum(1 for _ in reader)
        return row_count
    
    def count_data_rows(self) -> int:
        """
        计算CSV文件的数据行数（不包括标题行）
        
        Returns:
            int: CSV文件的数据行数
        """
        return max(0, self.count_rows() - 1)
    
    def read_header(self) -> List[str]:
        """
        读取CSV文件的标题行
        
        Returns:
            List[str]: 标题行列表
        """
        with open(self.file_path, 'r', encoding=self.encoding) as file:
            reader = csv.reader(file, delimiter=self.delimiter)
            header = next(reader, [])
        return header
    
    def read_row_by_index(self, index: int) -> Optional[List[str]]:
        """
        根据索引读取特定行（0为标题行）
        
        Args:
            index: 行索引（从0开始）
            
        Returns:
            Optional[List[str]]: 如果行存在，返回该行数据；否则返回None
        """
        if index < 0:
            raise ValueError("索引不能为负数")
            
        with open(self.file_path, 'r', encoding=self.encoding) as file:
            reader = csv.reader(file, delimiter=self.delimiter)
            for i, row in enumerate(reader):
                if i == index:
                    return row
        return None
    
    def read_all_rows(self) -> List[List[str]]:
        """
        读取CSV文件的所有行（包括标题行）
        
        Returns:
            List[List[str]]: 所有行的列表
        """
        with open(self.file_path, 'r', encoding=self.encoding) as file:
            reader = csv.reader(file, delimiter=self.delimiter)
            return list(reader)
    
    def read_all_data_rows(self) -> List[List[str]]:
        """
        读取CSV文件的所有数据行（不包括标题行）
        
        Returns:
            List[List[str]]: 所有数据行的列表
        """
        with open(self.file_path, 'r', encoding=self.encoding) as file:
            reader = csv.reader(file, delimiter=self.delimiter)
            next(reader, None)  # 跳过标题行
            return list(reader)
    
    def read_rows_iterator(self) -> Iterator[List[str]]:
        """
        返回一个迭代器，用于逐行读取CSV文件（包括标题行）
        
        Returns:
            Iterator[List[str]]: 行迭代器
        """
        with open(self.file_path, 'r', encoding=self.encoding) as file:
            reader = csv.reader(file, delimiter=self.delimiter)
            for row in reader:
                yield row
    
    def read_data_rows_iterator(self) -> Iterator[List[str]]:
        """
        返回一个迭代器，用于逐行读取CSV文件的数据行（不包括标题行）
        
        Returns:
            Iterator[List[str]]: 数据行迭代器
        """
        with open(self.file_path, 'r', encoding=self.encoding) as file:
            reader = csv.reader(file, delimiter=self.delimiter)
            next(reader, None)  # 跳过标题行
            for row in reader:
                yield row
    
    def read_as_dict_iterator(self) -> Iterator[Dict[str, str]]:
        """
        返回一个迭代器，将每行数据作为字典返回（键为标题行的值）
        
        Returns:
            Iterator[Dict[str, str]]: 字典行迭代器
        """
        with open(self.file_path, 'r', encoding=self.encoding) as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            for row in reader:
                yield dict(row)
    
    def get_column_values(self, column_name: str) -> List[str]:
        """
        获取指定列的所有值
        
        Args:
            column_name: 列名
            
        Returns:
            List[str]: 指定列的所有值
        """
        values = []
        with open(self.file_path, 'r', encoding=self.encoding) as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            for row in reader:
                if column_name in row:
                    values.append(row[column_name])
        return values
    
    def get_column_values_by_index(self, column_index: int) -> List[str]:
        """
        根据列索引获取指定列的所有值（不包括标题行）
        
        Args:
            column_index: 列索引（从0开始）
            
        Returns:
            List[str]: 指定列的所有值
        """
        if column_index < 0:
            raise ValueError("列索引不能为负数")
            
        values = []
        with open(self.file_path, 'r', encoding=self.encoding) as file:
            reader = csv.reader(file, delimiter=self.delimiter)
            next(reader, None)  # 跳过标题行
            for row in reader:
                if column_index < len(row):
                    values.append(row[column_index])
        return values


# 使用示例
if __name__ == "__main__":
    # 假设有一个名为data.csv的文件
    try:
        csv_processor = CSVProcessor("data.csv")
        
        # 获取行数
        print(f"总行数: {csv_processor.count_rows()}")
        print(f"数据行数: {csv_processor.count_data_rows()}")
        
        # 读取标题行
        print(f"标题行: {csv_processor.read_header()}")
        
        # 逐行读取数据
        print("\n逐行读取数据:")
        for i, row in enumerate(csv_processor.read_data_rows_iterator()):
            print(f"第{i+1}行: {row}")
            # 只打印前5行
            if i >= 4:
                print("...")
                break
        
        # 以字典形式读取
        print("\n以字典形式读取:")
        for i, row_dict in enumerate(csv_processor.read_as_dict_iterator()):
            print(f"第{i+1}行: {row_dict}")
            # 只打印前5行
            if i >= 4:
                print("...")
                break
                
    except Exception as e:
        print(f"错误: {e}")
        print("请确保data.csv文件存在并且格式正确") 