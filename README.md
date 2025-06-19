# Mark Excel - 智能表格数据整理工具 🧹✨

一个轻量、强大且易于使用的桌面应用，旨在帮助您快速清理和格式化来自各种来源的表格数据，并将其导出为干净的 Excel 或 CSV 文件。

![App Screenshot](https://i.imgur.com/your_screenshot.png)  <!-- 之后可以替换成真实的截图 -->

---

## 核心功能 🚀

*   **智能数据解析**:
    *   **多格式粘贴**: 直接从剪贴板粘贴 Markdown、CSV、TSV 格式的数据。
    *   **文件拖拽**: 将 `.txt`, `.csv`, `.tsv`, `.md` 文件拖入窗口即可加载。
    *   **智能检测**: 自动检测最可能的分隔符 (`\t`, `,`, `|`, `;`)。
    *   **自定义解析**: 手动设置表头行、要跳过的行数以及引号字符。

*   **强大的数据清理**:
    *   **一键清理**: 快速移除空行和重复行。
    *   **填充缺失值**: 将所有空白单元格填充为您指定的默认值。
    *   **列名规范化**: 自动将 `Column Name` 或 `column-name` 转换为标准的 `column_name` 格式。

*   **实时交互式编辑**:
    *   **实时预览**: 所有操作都会即时反映在预览表格中。
    *   **单元格编辑**: ✍️ 直接双击表格中的任何单元格来修改其内容。
    *   **行列管理**: 轻松删除选中的多行，或通过弹出窗口管理（删除）不再需要的列。

*   **灵活的导出选项**:
    *   **多种格式**: 导出为通用的 Excel (`.xlsx`) 或 CSV (`.csv`) 文件。
    *   **自动打开**: 可选择在导出后自动用默认程序打开文件，方便立刻查看。

*   **现代化与用户友好**:
    *   **多语言支持**: 🌐 无缝切换中文和英文界面。
    *   **主题自适应**: 自动适应系统的亮色/暗色模式，并美化表格样式。
    *   **配置记忆**: 自动保存您的设置（如语言、分隔符等），下次启动时无需重新配置。
    *   **悬浮提示**: 所有功能按钮都有清晰的鼠标悬浮提示，助您快速上手。

---

## 如何运行 🛠️

**环境要求**: Python 3.8+

1.  **克隆或下载项目**
    ```bash
    git clone https://github.com/your-username/mark-excel.git
    cd mark-excel
    ```

2.  **创建并激活虚拟环境**

    *   对于 **venv**:
        ```bash
        python -m venv venv
        # Windows
        .\venv\Scripts\activate
        # macOS / Linux
        source venv/bin/activate
        ```
    *   对于 **conda**:
        ```bash
        conda create -n markexcel python=3.9
        conda activate markexcel
        ```

3.  **安装依赖**
    在激活的虚拟环境中，运行以下命令来安装所有必需的库：
    ```bash
    pip install -r requirements.txt
    ```

4.  **启动应用**! 🎉
    ```bash
    python main.py
    ``` 