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
            target_size_kb = tool_parameters.get("target_size_kb", 200)
            quality = tool_parameters.get("quality", 85)
            output_format = tool_parameters.get("format", "auto")
            
            # 检查是否提供了图片文件或URL
            if not image_file and not image_url:
                yield self.create_text_message("错误：请提供图片文件或图片链接")
                return
            
            # 处理图片文件上传
            if image_file:
                logger.info("开始处理上传的图片文件")
                logger.info(f"image_file类型: {type(image_file)}")
                
                # 检查是否为File类型对象
                if isinstance(image_file, File):
                    logger.info("检测到File类型对象")
                    # 验证文件类型
                    if image_file.type != "image":
                        yield self.create_text_message(f"错误：文件类型不是图片，当前类型: {image_file.type}")
                        return
                    
                    # 直接使用blob属性获取图片数据
                    image_data = image_file.blob
                    logger.info(f"从File.blob获取图片数据，类型: {type(image_data)}, 长度: {len(image_data)}")
                    
                else:
                    # 兼容其他类型的处理逻辑
                    logger.info("检测到非File类型对象，使用兼容处理逻辑")
                    
                    if hasattr(image_file, 'content'):
                        # 如果是文件对象，直接读取内容
                        logger.info("检测到文件对象，使用content属性")
                        image_data = image_file.content
                        logger.info(f"content类型: {type(image_data)}, 长度: {len(image_data) if hasattr(image_data, '__len__') else '未知'}")
                    elif isinstance(image_file, str):
                        # 如果是base64字符串，解码
                        logger.info("检测到字符串，尝试base64解码")
                        image_data = base64.b64decode(image_file)
                        logger.info(f"解码后长度: {len(image_data)}")
                    elif isinstance(image_file, tuple):
                        # 如果是元组类型，通常是 (filename, file_content, content_type) 格式
                        logger.info("检测到元组类型文件对象")
                        if len(image_file) >= 2:
                            # 第二个元素通常是文件内容
                            image_data = image_file[1]
                            logger.info(f"从元组中提取文件内容，类型: {type(image_data)}, 长度: {len(image_data) if hasattr(image_data, '__len__') else '未知'}")
                        else:
                            raise ValueError("元组格式不正确，无法提取文件内容")
                    elif hasattr(image_file, 'read'):
                        # 如果有read方法，尝试读取
                        logger.info("检测到有read方法的文件对象")
                        image_data = image_file.read()
                        logger.info(f"read后类型: {type(image_data)}, 长度: {len(image_data) if hasattr(image_data, '__len__') else '未知'}")
                    else:
                        # 其他情况，尝试转换为字节
                        logger.info(f"其他类型，尝试转换为字节: {type(image_file)}")
                        try:
                            image_data = bytes(image_file)
                            logger.info(f"转换成功，长度: {len(image_data)}")
                        except Exception as conversion_error:
                            logger.error(f"转换失败: {conversion_error}")
                            raise ValueError(f"无法将 {type(image_file)} 类型的文件对象转换为字节数据")
                
                # 打开图片
                logger.info("尝试打开图片")
                image = Image.open(io.BytesIO(image_data))
                logger.info(f"图片格式: {image.format}, 模式: {image.mode}")
                original_size = len(image_data)
                original_format = image.format or "JPEG"
                logger.info(f"原始大小: {original_size} 字节, 格式: {original_format}")
                
                # 验证图片尺寸
                logger.info(f"文件图片尺寸验证 - width: {type(image.width)}, height: {type(image.height)}")
                logger.info(f"文件图片尺寸验证 - size: {type(image.size)}")
                
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
                    
                    # 验证图片尺寸
                    logger.info(f"URL图片尺寸验证 - width: {type(image.width)}, height: {type(image.height)}")
                    logger.info(f"URL图片尺寸验证 - size: {type(image.size)}")
                    
                except requests.RequestException as e:
                    logger.error(f"下载图片失败: {str(e)}")
                    yield self.create_text_message(f"下载图片失败: {str(e)}")
                    return
            
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
                "message": "图片压缩成功",
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
            
            # 将压缩后的图片转换为字节数据
            img_buffer = io.BytesIO()
            compressed_image.save(img_buffer, format=compression_info["format_used"])
            compressed_bytes = img_buffer.getvalue()
            
            # 返回压缩信息和压缩后的图片数据，参考demo/image.py的返回方式
            yield self.create_json_message(info)
            yield self.create_blob_message(blob=compressed_bytes, meta={"mime_type": compression_info["mime_type"]})
            
        except Exception as e:
            logger.error(f"图片压缩失败: {str(e)}")
            yield self.create_text_message(f"图片压缩失败: {str(e)}")
    
    def _compress_image(self, image: Image.Image, target_size_kb: int, quality: int, 
                       output_format: str, original_format: str) -> tuple[Image.Image, dict]:
        """压缩图片的核心逻辑"""
        logger.info(f"开始压缩图片，参数类型验证:")
        logger.info(f"  target_size_kb: {type(target_size_kb)} = {target_size_kb}")
        logger.info(f"  quality: {type(quality)} = {quality}")
        logger.info(f"  output_format: {type(output_format)} = {output_format}")
        logger.info(f"  original_format: {type(original_format)} = {original_format}")
        
        target_size_bytes = target_size_kb * 1024
        current_quality = quality
        current_image = image.copy()
        
        logger.info(f"计算后的target_size_bytes: {type(target_size_bytes)} = {target_size_bytes}")
        
        # 获取图片尺寸，确保是整数类型
        try:
            img_width = int(current_image.width)
            img_height = int(current_image.height)
            logger.info(f"图片尺寸: {img_width} x {img_height}")
        except (ValueError, TypeError) as e:
            logger.error(f"获取图片尺寸失败: {e}, 类型: {type(current_image.width)}, {type(current_image.height)}")
            # 尝试使用size属性
            try:
                img_width, img_height = current_image.size
                img_width = int(img_width)
                img_height = int(img_height)
                logger.info(f"使用size属性获取图片尺寸: {img_width} x {img_height}")
            except Exception as e2:
                logger.error(f"使用size属性获取图片尺寸也失败: {e2}")
                raise ValueError(f"无法获取图片尺寸: {e2}")
        
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
        
        # 尝试通过调整质量来达到目标大小
        while current_quality > 60:
            img_buffer = io.BytesIO()
            
            if format_used == "JPEG":
                current_image.save(img_buffer, format="JPEG", quality=current_quality, optimize=True)
            elif format_used == "PNG":
                current_image.save(img_buffer, format="PNG", optimize=True)
            elif format_used == "WEBP":
                current_image.save(img_buffer, format="WEBP", quality=current_quality, lossless=False)
            else:
                current_image.save(img_buffer, format=format_used, quality=current_quality, optimize=True)
            
            current_size = len(img_buffer.getvalue())
            
            if current_size <= target_size_bytes:
                break
            
            current_quality -= 5
        
        # 如果质量调整后仍然太大，尝试调整尺寸
        was_resized = False
        if current_size > target_size_bytes:
            # 计算需要缩放的倍数
            scale_factor = (target_size_bytes / current_size) ** 0.5
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)
            
            logger.info(f"调整图片尺寸: {img_width}x{img_height} -> {new_width}x{new_height}")
            current_image = current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            was_resized = True
            
            # 重新保存并检查大小
            img_buffer = io.BytesIO()
            if format_used == "JPEG":
                current_image.save(img_buffer, format="JPEG", quality=current_quality, optimize=True)
            elif format_used == "PNG":
                current_image.save(img_buffer, format="PNG", optimize=True)
            elif format_used == "WEBP":
                current_image.save(img_buffer, format="WEBP", quality=current_quality, lossless=False)
            else:
                current_image.save(img_buffer, format=format_used, quality=current_quality, optimize=True)
            
            current_size = len(img_buffer.getvalue())
        
        compression_info = {
            "size": current_size,
            "format_used": format_used,
            "width": img_width,
            "height": img_height,
            "quality_used": current_quality,
            "was_resized": was_resized,
            "mime_type": mime_type
        }
        
        return current_image, compression_info
