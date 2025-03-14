from csv_processor import CSVProcessor

# 创建CSV处理器实例
csv_processor = CSVProcessor("data.csv")

# 获取特定列的所有值
print("=== 按列名获取数据 ===")
names = csv_processor.get_column_values("姓名")
print(f"所有姓名: {names}")

ages = csv_processor.get_column_values("年龄")
print(f"所有年龄: {ages}")

cities = csv_processor.get_column_values("城市")
print(f"所有城市: {cities}")

# 按列索引获取数据
print("\n=== 按列索引获取数据 ===")
column_0 = csv_processor.get_column_values_by_index(0)  # 姓名列
print(f"第1列数据 (姓名): {column_0}")

column_1 = csv_processor.get_column_values_by_index(1)  # 年龄列
print(f"第2列数据 (年龄): {column_1}")

# 获取特定行的数据
print("\n=== 获取特定行的数据 ===")
header = csv_processor.read_row_by_index(0)
print(f"标题行: {header}")

row_3 = csv_processor.read_row_by_index(3)
print(f"第3行数据: {row_3}")

# 计算行数
print("\n=== 行数统计 ===")
print(f"总行数: {csv_processor.count_rows()}")
print(f"数据行数: {csv_processor.count_data_rows()}") 