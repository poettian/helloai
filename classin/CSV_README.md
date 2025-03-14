# CSV处理器

这是一个用于处理CSV文件的Python类，提供了多种方法来读取和分析CSV数据。

## 功能特点

- 逐行读取CSV数据
- 计算CSV文件的行数（总行数和数据行数）
- 读取特定行或列的数据
- 支持以列表或字典形式读取数据
- 支持按列名或列索引获取数据
- 提供迭代器接口，适合处理大型CSV文件

## 使用方法

### 基本用法

```python
from csv_processor import CSVProcessor

# 创建CSV处理器实例
csv_processor = CSVProcessor("data.csv")

# 获取行数
total_rows = csv_processor.count_rows()
data_rows = csv_processor.count_data_rows()

# 读取标题行
header = csv_processor.read_header()

# 读取特定行
row_3 = csv_processor.read_row_by_index(3)  # 获取第3行数据
```

### 逐行读取数据

```python
# 逐行读取所有数据（包括标题行）
for row in csv_processor.read_rows_iterator():
    print(row)

# 逐行读取数据行（不包括标题行）
for row in csv_processor.read_data_rows_iterator():
    print(row)

# 以字典形式逐行读取数据
for row_dict in csv_processor.read_as_dict_iterator():
    print(row_dict)
```

### 获取列数据

```python
# 按列名获取数据
names = csv_processor.get_column_values("姓名")
ages = csv_processor.get_column_values("年龄")

# 按列索引获取数据
first_column = csv_processor.get_column_values_by_index(0)
second_column = csv_processor.get_column_values_by_index(1)
```

### 读取所有数据

```python
# 读取所有行（包括标题行）
all_rows = csv_processor.read_all_rows()

# 读取所有数据行（不包括标题行）
all_data_rows = csv_processor.read_all_data_rows()
```

## 参数说明

在创建CSVProcessor实例时，可以指定以下参数：

- `file_path`：CSV文件路径（必需）
- `encoding`：文件编码，默认为'utf-8'
- `delimiter`：CSV分隔符，默认为逗号','

示例：
```python
# 使用自定义参数创建CSV处理器
csv_processor = CSVProcessor(
    file_path="data.csv",
    encoding="gbk",
    delimiter=";"
)
```

## 注意事项

- 文件必须存在且为CSV格式
- 默认假设CSV文件的第一行为标题行
- 对于大型CSV文件，建议使用迭代器方法而不是一次性读取所有数据 