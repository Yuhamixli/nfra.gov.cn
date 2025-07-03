# ChromeDriver 本地缓存目录

此目录用于存储本地ChromeDriver文件，避免每次启动时都需要重新下载。

## 目录结构

```
drivers/
├── README.md              # 本文件
└── chromedriver.exe       # ChromeDriver可执行文件 (Windows)
```

## 设置说明

### 1. 自动设置（推荐）

使用提供的setup_driver.py脚本：

```bash
# 检查当前状态
python setup_driver.py status

# 下载并设置ChromeDriver
python setup_driver.py download

# 测试是否正常工作
python setup_driver.py test
```

### 2. 手动设置

1. **下载ChromeDriver**
   - 访问 https://chromedriver.chromium.org/
   - 下载与你的Chrome浏览器版本匹配的ChromeDriver
   - 或者使用 https://googlechromelabs.github.io/chrome-for-testing/

2. **放置文件**
   - 将下载的 `chromedriver.exe` 放入此目录
   - 确保文件名为 `chromedriver.exe`（Windows）或 `chromedriver`（Linux/Mac）

3. **设置权限**（Linux/Mac）
   ```bash
   chmod +x drivers/chromedriver
   ```

## 配置说明

相关配置在 `config.py` 中的 `WEBDRIVER_CONFIG`：

```python
WEBDRIVER_CONFIG = {
    'local_driver_dir': 'drivers',      # 本地driver目录
    'driver_filename': 'chromedriver.exe',  # driver文件名
    'use_local_driver': True,           # 优先使用本地driver
    'auto_download': True,              # 自动下载（如果本地不存在）
    'cache_valid_days': 7,             # 缓存有效期（天）
}
```

## 优势

- ✅ **快速启动**：避免每次启动时的网络下载
- ✅ **离线工作**：无需网络连接即可使用
- ✅ **稳定性**：避免网络问题导致的启动失败
- ✅ **版本控制**：可以固定使用特定版本的ChromeDriver

## 工作原理

1. 程序启动时，优先检查本地 `drivers/` 目录
2. 如果找到有效的ChromeDriver，直接使用
3. 如果没有找到，根据配置决定是否自动下载
4. 下载完成后，会自动复制到本地目录以备后用

## 故障排除

### 问题1：权限不足
```bash
# Linux/Mac
chmod +x drivers/chromedriver

# Windows通常不需要额外设置
```

### 问题2：版本不匹配
```bash
# 清理旧版本
python setup_driver.py clean

# 重新下载
python setup_driver.py download
```

### 问题3：测试失败
```bash
# 检查状态
python setup_driver.py status

# 重新测试
python setup_driver.py test
```

## 注意事项

1. **版本兼容**：ChromeDriver版本必须与Chrome浏览器版本匹配
2. **定期更新**：建议每隔一段时间更新ChromeDriver
3. **文件名称**：确保文件名正确（Windows: `chromedriver.exe`，Linux/Mac: `chromedriver`）
4. **执行权限**：Linux/Mac系统需要设置执行权限

## 维护

建议定期检查并更新ChromeDriver：

```bash
# 检查当前状态
python setup_driver.py status

# 如果Chrome浏览器更新了，重新下载匹配的driver
python setup_driver.py clean
python setup_driver.py download
``` 