# Image Press - Dify 图片压缩插件

## 概述

Image Press 是一个强大的 Dify 插件，专门用于图片压缩。它可以将图片压缩到指定大小，同时保持最佳质量。支持多种图片格式，包括 JPEG、PNG 和 WebP。

## 功能特性

- 🖼️ **智能压缩**：自动调整质量和尺寸以达到目标文件大小
- 📏 **精确控制**：支持指定目标大小（50KB - 8192KB）
- 🎯 **质量优化**：可调节压缩质量（60-95）
- 🔄 **格式支持**：支持 JPEG、PNG、WebP 等格式
- 🌐 **URL 支持**：直接通过图片 URL 进行压缩
- 📊 **详细反馈**：提供压缩比例、尺寸变化等详细信息

## 安装方法

### 方法一：通过 GitHub 仓库安装

1. 在 Dify 工作区中，进入插件管理
2. 选择"从 GitHub 安装"
3. 输入仓库地址：`https://github.com/your-username/image_press`
4. 点击安装

### 方法二：通过插件包安装

1. 下载 `.difypkg` 文件
2. 在 Dify 工作区中上传插件包
3. 完成安装

## 使用方法

### 基本用法

在 Dify 应用中，你可以这样使用图片压缩工具：

```
请帮我压缩这张图片：https://example.com/image.jpg
目标大小：200KB
质量：85
输出格式：自动
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `image_url` | string | ✅ | - | 需要压缩的图片链接 |
| `target_size_kb` | integer | ❌ | 200 | 目标文件大小（KB），范围：50-8192 |
| `quality` | integer | ❌ | 85 | 初始压缩质量，范围：60-95 |
| `format` | string | ❌ | auto | 输出格式：auto、jpeg、png、webp |

### 使用示例

#### 示例 1：基本压缩
```
图片链接：https://example.com/photo.jpg
目标大小：500KB
质量：90
格式：自动
```

#### 示例 2：高质量压缩
```
图片链接：https://example.com/portrait.png
目标大小：1000KB
质量：95
格式：PNG
```

#### 示例 3：小文件压缩
```
图片链接：https://example.com/icon.webp
目标大小：100KB
质量：80
格式：JPEG
```

## 技术实现

### 压缩算法

1. **质量调整**：首先尝试通过调整 JPEG 质量参数来达到目标大小
2. **尺寸缩放**：如果质量调整后仍然过大，则按比例缩小图片尺寸
3. **格式优化**：根据原始格式和用户选择，选择最优的输出格式

### 支持的图片格式

- **输入格式**：JPEG、PNG、WebP、BMP、TIFF 等
- **输出格式**：JPEG、PNG、WebP
- **自动选择**：根据原始格式自动选择最佳输出格式

## 开发环境

### 系统要求

- Python 3.12+
- Dify 平台支持

### 依赖包

```
dify_plugin>=0.2.0,<0.3.0
Pillow>=10.0.0
requests>=2.31.0
```

### 本地开发

1. 克隆仓库
```bash
git clone https://github.com/your-username/image_press.git
cd image_press
```

2. 安装依赖
```bash
uv pip install -r requirements.txt
```

3. 运行插件
```bash
python -m main
```

## 注意事项

1. **网络要求**：需要能够访问图片 URL
2. **内存使用**：大图片可能需要较多内存
3. **处理时间**：高分辨率图片压缩可能需要较长时间
4. **格式限制**：某些特殊格式可能无法处理

## 常见问题

### Q: 为什么压缩后的图片质量很差？
A: 可以尝试提高 `quality` 参数值，或者增加 `target_size_kb` 值。

### Q: 支持哪些图片格式？
A: 支持常见的图片格式，包括 JPEG、PNG、WebP、BMP、TIFF 等。

### Q: 压缩失败怎么办？
A: 检查图片 URL 是否可访问，网络连接是否正常，以及参数设置是否合理。

### Q: 如何获得最佳压缩效果？
A: 建议先使用默认参数测试，然后根据结果调整质量和目标大小参数。

## 更新日志

### v0.0.1 (2025-09-02)
- 🎉 初始版本发布
- ✨ 支持基本图片压缩功能
- 🌐 支持 URL 图片下载
- 📊 提供详细的压缩信息

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个插件！

## 许可证

本项目采用 MIT 许可证。

## 联系方式

- 作者：liangmj
- 项目地址：https://github.com/your-username/image_press
- 问题反馈：https://github.com/your-username/image_press/issues



