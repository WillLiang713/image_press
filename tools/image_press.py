import base64
import io
import logging
from collections.abc import Generator
from typing import Any
from PIL import Image
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File  # 添加File类型导入

# 配置日志
logger = logging.getLogger(__name__)

class ImagePressTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # 获取参数
            image_file = tool_parameters.get("image_input", None)
            image_url = tool_parameters.get("image_url", "")
            
            # 检查是否提供了图片文件或URL
            if not image_file and not image_url:
                yield self.create_text_message("错误：请提供图片文件或图片链接")
                return
            
            # 处理图片文件上传 - 简化版本
            if image_file:
                logger.info("开始处理上传的图片文件")
                
                # 获取图片数据
                if isinstance(image_file, File):
                    if image_file.type != "image":
                        yield self.create_text_message(f"错误：文件类型不是图片")
                        return
                    image_data = image_file.blob
                elif hasattr(image_file, 'content'):
                    image_data = image_file.content
                elif hasattr(image_file, 'read'):
                    image_data = image_file.read()
                else:
                    yield self.create_text_message("错误：无法读取上传的文件")
                    return
                
                # 打开图片
                image = Image.open(io.BytesIO(image_data))
                original_size = len(image_data)
                original_format = image.format or "JPEG"
                
            # 处理图片URL
            elif image_url:
                logger.info(f"开始下载图片: {image_url}")
                try:
                    response = requests.get(image_url, timeout=30)
                    response.raise_for_status()
                    
                    # 打开图片
                    image = Image.open(io.BytesIO(response.content))
                    original_size = len(response.content)
                    original_format = image.format or "JPEG"
                    
                except requests.RequestException as e:
                    logger.error(f"下载图片失败: {str(e)}")
                    yield self.create_text_message(f"下载图片失败: {str(e)}")
                    return
            
            # 统一压缩到1MB以下
            target_size_kb = 1024  # 1MB = 1024KB
            quality = 85  # 固定质量
            output_format = "auto"  # 自动格式
            
            logger.info(f"统一压缩参数: 目标大小={target_size_kb}KB, 质量={quality}")
            
            # 压缩图片
            compressed_image, compression_info = self._compress_image(
                image, 
                target_size_kb, 
                quality, 
                output_format,
                original_format
            )
            
            # 计算压缩比
            compression_ratio = (1 - compression_info["size"] / original_size) * 100 if original_size else 0.0
            
            # 返回压缩信息
            info = {
                "status": "success",
                "message": "图片压缩成功（已压缩到1MB以下）",
                "input_type": "file" if image_file else "url",
                "original_size_kb": round(original_size / 1024, 2),
                "compressed_size_kb": round(compression_info["size"] / 1024, 2),
                "compression_ratio": round(compression_ratio, 1),
                "format_used": compression_info["format_used"],
                "width": compression_info["width"],
                "height": compression_info["height"],
                "quality_used": compression_info["quality_used"],
                "was_resized": compression_info["was_resized"],
                "mime_type": compression_info["mime_type"]
            }
            
            # 直接使用压缩过程中已经生成的图片数据，避免重复保存
            compressed_bytes = compression_info["image_data"]
            
            # 返回压缩信息和压缩后的图片数据
            yield self.create_json_message(info)
            yield self.create_blob_message(blob=compressed_bytes, meta={"mime_type": compression_info["mime_type"]})
            
        except Exception as e:
            logger.error(f"图片压缩失败: {str(e)}")
            yield self.create_text_message(f"图片压缩失败: {str(e)}")
    
    def _compress_image(self, image: Image.Image, target_size_kb: int, quality: int, 
                       output_format: str, original_format: str) -> tuple[Image.Image, dict]:
        """简化的图片压缩逻辑"""
        logger.info(f"开始压缩图片到 {target_size_kb}KB")
        
        target_size_bytes = target_size_kb * 1024
        current_image = image.copy()
        width, height = current_image.size
        
        # 确定输出格式
        if output_format == "auto":
            if original_format in ["JPEG", "JPG"]:
                format_used = "JPEG"
                mime_type = "image/jpeg"
            elif original_format == "PNG":
                format_used = "PNG"
                mime_type = "image/png"
            elif original_format == "WEBP":
                format_used = "WEBP"
                mime_type = "image/webp"
            else:
                format_used = "JPEG"
                mime_type = "image/jpeg"
        else:
            format_used = output_format.upper()
            mime_type = f"image/{output_format.lower()}"
        
        was_resized = False
        
        # 如果是大图片，先缩小尺寸
        if width * height > 3000000:  # 大于3MP直接缩小
            scale = 0.7
            new_width = int(width * scale)
            new_height = int(height * scale)
            current_image = current_image.resize((new_width, new_height), Image.Resampling.BILINEAR)
            width, height = new_width, new_height
            was_resized = True
            logger.info(f"大图片预缩放到: {width}x{height}")
        
        # 简单的质量调整循环
        for attempt_quality in [quality, 75, 65, 60]:
            img_buffer = io.BytesIO()
            
            if format_used == "PNG":
                current_image.save(img_buffer, format="PNG", optimize=True)
            elif format_used == "JPEG":
                current_image.save(img_buffer, format="JPEG", quality=attempt_quality, optimize=True)
            elif format_used == "WEBP":
                current_image.save(img_buffer, format="WEBP", quality=attempt_quality, lossless=False)
            else:
                current_image.save(img_buffer, format=format_used, quality=attempt_quality, optimize=True)
            
            image_data = img_buffer.getvalue()
            current_size = len(image_data)
            
            # 如果大小满足要求，直接返回
            if current_size <= target_size_bytes:
                logger.info(f"压缩成功: {current_size} bytes, 质量: {attempt_quality}")
                break
        
        # 如果还是太大，最后尝试缩小尺寸
        if current_size > target_size_bytes:
            scale = 0.8
            new_width = max(int(width * scale), 200)  # 最小宽度200
            new_height = max(int(height * scale), 200)  # 最小高度200
            
            current_image = current_image.resize((new_width, new_height), Image.Resampling.BILINEAR)
            width, height = new_width, new_height
            was_resized = True
            
            # 重新保存
            img_buffer = io.BytesIO()
            if format_used == "PNG":
                current_image.save(img_buffer, format="PNG", optimize=True)
            elif format_used == "JPEG":
                current_image.save(img_buffer, format="JPEG", quality=60, optimize=True)
            elif format_used == "WEBP":
                current_image.save(img_buffer, format="WEBP", quality=60, lossless=False)
            else:
                current_image.save(img_buffer, format=format_used, quality=60, optimize=True)
            
            image_data = img_buffer.getvalue()
            attempt_quality = 60
            logger.info(f"最终缩放到: {width}x{height}")
        
        compression_info = {
            "size": len(image_data),
            "format_used": format_used,
            "width": width,
            "height": height,
            "quality_used": attempt_quality,
            "was_resized": was_resized,
            "mime_type": mime_type,
            "image_data": image_data
        }
        
        return current_image, compression_info
