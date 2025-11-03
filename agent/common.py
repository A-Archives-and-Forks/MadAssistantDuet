# -*- coding: utf-8 -*-
"""
通用自定义动作模块
包含各种常用的自定义 Action
"""

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import time
import logging
import json
import os
from datetime import datetime

# 获取日志记录器
logger = logging.getLogger(__name__)


@AgentServer.custom_action("ResetCharacterPosition")
class ResetCharacterPosition(CustomAction):
    """
    复位角色位置的自定义动作
    
    执行流程：
    1. 按 ESC 键打开菜单
    2. OCR 识别并点击"设置"
    3. 模板匹配并点击"其他.jpg"
    4. OCR 识别并点击"复位角色"
    5. OCR 识别并点击"确定"
    
    参数示例：
    {
        "template_path": "common/其他.png",  // 模板图片路径（可选，默认为"common/其他.png"）
        "wait_delay": 500,                   // 每步操作后的等待时间（毫秒，可选，默认500ms）
        "retry_times": 10,                   // 识别重试次数（可选，默认10次）
        "retry_interval": 500                // 重试间隔（毫秒，可选，默认500ms）
    }
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        try:
            # 解析参数
            if isinstance(argv.custom_action_param, str):
                params = json.loads(argv.custom_action_param)
            elif isinstance(argv.custom_action_param, dict):
                params = argv.custom_action_param
            else:
                params = {}
            
            # 获取参数
            template_path = params.get("template_path", "common/其他.png")
            wait_delay = params.get("wait_delay", 500)  # 默认每步等待 500ms
            retry_times = params.get("retry_times", 10)  # 默认重试 10 次
            retry_interval = params.get("retry_interval", 500)  # 默认重试间隔 500ms
            
            logger.info("=" * 60)
            logger.info("[ResetCharacterPosition] 开始执行角色复位流程")
            logger.info(f"  模板图片: {template_path}")
            logger.info(f"  等待延迟: {wait_delay}ms")
            logger.info(f"  重试次数: {retry_times}")
            logger.info(f"  重试间隔: {retry_interval}ms")
            logger.info("=" * 60)
            
            # 步骤 1: 按 ESC 键
            if not self._step1_press_esc(context, wait_delay):
                return False
            
            # 步骤 2: OCR 识别并点击"设置"
            if not self._step2_click_settings(context, wait_delay, retry_times, retry_interval):
                return False
            
            # 步骤 3: 模板匹配并点击"其他"
            if not self._step3_click_other(context, template_path, wait_delay, retry_times, retry_interval):
                return False
            
            # 步骤 4: OCR 识别并点击"复位角色"
            if not self._step4_click_reset_character(context, wait_delay, retry_times, retry_interval):
                return False
            
            # 步骤 5: OCR 识别并点击"确定"
            if not self._step5_click_confirm(context, wait_delay, retry_times, retry_interval):
                return False
            
            logger.info("[ResetCharacterPosition] [OK] 角色复位流程执行完成")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"[ResetCharacterPosition] 执行失败: {e}", exc_info=True)
            return False
    
    def _step1_press_esc(self, context: Context, wait_delay: int) -> bool:
        """步骤 1: 按 ESC 键打开菜单"""
        logger.info("[ResetCharacterPosition] 步骤 1: 按 ESC 键...")
        
        try:
            # ESC 键的虚拟键码是 27
            logger.info(f"  [DEBUG] 调用 post_click_key(27)...")
            click_job = context.tasker.controller.post_click_key(27)
            click_job.wait()
            logger.info(f"  [DEBUG] post_click_key(27) 完成")
            
            logger.info(f"  [OK] ESC 键已按下，等待 {wait_delay}ms...")
            time.sleep(wait_delay / 1000.0)
            
            # 刷新截图
            context.tasker.controller.post_screencap().wait()
            
            return True
            
        except Exception as e:
            logger.error(f"  [X] 按 ESC 键失败: {e}", exc_info=True)
            return False
    
    def _step2_click_settings(self, context: Context, wait_delay: int, retry_times: int, retry_interval: int) -> bool:
        """步骤 2: OCR 识别并点击"设置" (带重试机制)"""
        logger.info("[ResetCharacterPosition] 步骤 2: OCR 识别并点击'设置'...")
        
        for attempt in range(1, retry_times + 1):
            try:
                logger.info(f"  尝试 {attempt}/{retry_times}: OCR 识别'设置'...")
                
                # 刷新截图
                context.tasker.controller.post_screencap().wait()
                image = context.tasker.controller.cached_image
                
                # 使用预定义节点 OCR_Settings (在 resetPosition.json 中定义)
                reco_result = context.run_recognition(
                    "OCR_Settings",
                    image
                )
                
                if not reco_result or not reco_result.box or reco_result.box.w == 0:
                    logger.warning(f"  尝试 {attempt}/{retry_times}: 未找到'设置'文字")
                    
                    # 如果不是最后一次尝试，等待后重试
                    if attempt < retry_times:
                        logger.info(f"  等待 {retry_interval}ms 后重试...")
                        time.sleep(retry_interval / 1000.0)
                        continue
                    else:
                        logger.error(f"  [X] 已达最大重试次数 ({retry_times})")
                        return False
                
                logger.info(f"  [OK] 找到'设置': box=({reco_result.box.x}, {reco_result.box.y}, {reco_result.box.w}, {reco_result.box.h})")
                
                # 点击识别框的中心
                click_x = reco_result.box.x + reco_result.box.w // 2
                click_y = reco_result.box.y + reco_result.box.h // 2
                
                click_job = context.tasker.controller.post_click(click_x, click_y)
                click_job.wait()
                
                logger.info(f"  [OK] 已点击'设置'，等待 {wait_delay}ms...")
                time.sleep(wait_delay / 1000.0)
                
                # 刷新截图 - 添加延迟确保缓存更新
                context.tasker.controller.post_screencap().wait()
                
                return True
                
            except Exception as e:
                logger.error(f"  尝试 {attempt}/{retry_times} [X] 点击'设置'失败: {e}", exc_info=True)
                if attempt < retry_times:
                    time.sleep(retry_interval / 1000.0)
                else:
                    return False
        
        return False
    
    def _step3_click_other(self, context: Context, template_path: str, wait_delay: int, retry_times: int, retry_interval: int) -> bool:
        """步骤 3: 模板匹配并点击"其他" (带重试机制)"""
        logger.info(f"[ResetCharacterPosition] 步骤 3: 模板匹配并点击'{template_path}'...")
        
        for attempt in range(1, retry_times + 1):
            try:
                logger.info(f"  尝试 {attempt}/{retry_times}: 模板匹配'{template_path}'...")
                
                # 刷新截图
                context.tasker.controller.post_screencap().wait()
                image = context.tasker.controller.cached_image
                
                # 使用预定义节点 Template_Other (在 resetPosition.json 中定义)
                # 如果需要动态模板路径,使用 pipeline_override 覆盖
                reco_result = context.run_recognition(
                    "Template_Other",
                    image,
                    pipeline_override={
                        "Template_Other": {
                            "template": template_path
                        }
                    } if template_path != "common/其他.png" else {}
                )
                
                if not reco_result or not reco_result.box or reco_result.box.w == 0:
                    logger.warning(f"  尝试 {attempt}/{retry_times}: 未找到模板'{template_path}'")
                    
                    # 如果不是最后一次尝试，等待后重试
                    if attempt < retry_times:
                        logger.info(f"  等待 {retry_interval}ms 后重试...")
                        time.sleep(retry_interval / 1000.0)
                        continue
                    else:
                        logger.error(f"  [X] 已达最大重试次数 ({retry_times})")
                        return False
                
                logger.info(f"  [OK] 找到模板: box=({reco_result.box.x}, {reco_result.box.y}, {reco_result.box.w}, {reco_result.box.h})")
                
                # 点击识别框的中心
                click_x = reco_result.box.x + reco_result.box.w // 2
                click_y = reco_result.box.y + reco_result.box.h // 2
                
                click_job = context.tasker.controller.post_click(click_x, click_y)
                click_job.wait()
                
                logger.info(f"  [OK] 已点击'{template_path}'，等待 {wait_delay}ms...")
                time.sleep(wait_delay / 1000.0)
                
                # 刷新截图
                context.tasker.controller.post_screencap().wait()
                return True
                
            except Exception as e:
                logger.error(f"  尝试 {attempt}/{retry_times} [X] 点击'{template_path}'失败: {e}", exc_info=True)
                if attempt < retry_times:
                    time.sleep(retry_interval / 1000.0)
                else:
                    return False
        
        return False
    
    def _step4_click_reset_character(self, context: Context, wait_delay: int, retry_times: int, retry_interval: int) -> bool:
        """步骤 4: OCR 识别并点击"复位角色" (带重试机制)"""
        logger.info("[ResetCharacterPosition] 步骤 4: OCR 识别并点击'复位角色'...")
        
        for attempt in range(1, retry_times + 1):
            try:
                logger.info(f"  尝试 {attempt}/{retry_times}: OCR 识别'复位角色'...")
                
                # 刷新截图
                context.tasker.controller.post_screencap().wait()
                image = context.tasker.controller.cached_image
                
                # 使用预定义节点 OCR_ResetCharacter (在 resetPosition.json 中定义)
                reco_result = context.run_recognition(
                    "OCR_ResetCharacter",
                    image
                )
                
                if not reco_result or not reco_result.box or reco_result.box.w == 0:
                    logger.warning(f"  尝试 {attempt}/{retry_times}: 未找到'复位角色'文字")
                    
                    # 如果不是最后一次尝试，等待后重试
                    if attempt < retry_times:
                        logger.info(f"  等待 {retry_interval}ms 后重试...")
                        time.sleep(retry_interval / 1000.0)
                        continue
                    else:
                        logger.error(f"  [X] 已达最大重试次数 ({retry_times})")
                        return False
                
                logger.info(f"  [OK] 找到'复位角色': box=({reco_result.box.x}, {reco_result.box.y}, {reco_result.box.w}, {reco_result.box.h})")
                
                # 点击识别框的中心
                click_x = reco_result.box.x + reco_result.box.w // 2
                click_y = reco_result.box.y + reco_result.box.h // 2
                
                click_job = context.tasker.controller.post_click(click_x, click_y)
                click_job.wait()
                
                logger.info(f"  [OK] 已点击'复位角色'，等待 {wait_delay}ms...")
                time.sleep(wait_delay / 1000.0)
                
                # 刷新截图
                context.tasker.controller.post_screencap().wait()
                return True
                
            except Exception as e:
                logger.error(f"  尝试 {attempt}/{retry_times} [X] 点击'复位角色'失败: {e}", exc_info=True)
                if attempt < retry_times:
                    time.sleep(retry_interval / 1000.0)
                else:
                    return False
        
        return False
    
    def _step5_click_confirm(self, context: Context, wait_delay: int, retry_times: int, retry_interval: int) -> bool:
        """步骤 5: OCR 识别并点击"确定" (带重试机制)"""
        logger.info("[ResetCharacterPosition] 步骤 5: OCR 识别并点击'确定'...")
        
        for attempt in range(1, retry_times + 1):
            try:
                logger.info(f"  尝试 {attempt}/{retry_times}: OCR 识别'确定'...")
                
                # 刷新截图
                context.tasker.controller.post_screencap().wait()
                image = context.tasker.controller.cached_image
                reco_result = context.run_recognition(
                    "OCR_Confirm",
                    image
                )
                
                if not reco_result or not reco_result.box or reco_result.box.w == 0:
                    logger.warning(f"  尝试 {attempt}/{retry_times}: 未找到'确定'文字")
                    
                    # 如果不是最后一次尝试，等待后重试
                    if attempt < retry_times:
                        logger.info(f"  等待 {retry_interval}ms 后重试...")
                        time.sleep(retry_interval / 1000.0)
                        continue
                    else:
                        logger.error(f"  [X] 已达最大重试次数 ({retry_times})")
                        return False
                
                logger.info(f"  [OK] 找到'确定': box=({reco_result.box.x}, {reco_result.box.y}, {reco_result.box.w}, {reco_result.box.h})")
                
                # 点击识别框的中心
                click_x = reco_result.box.x + reco_result.box.w // 2
                click_y = reco_result.box.y + reco_result.box.h // 2
                
                click_job = context.tasker.controller.post_click(click_x, click_y)
                click_job.wait()
                
                logger.info(f"  [OK] 已点击'确定'，等待 {wait_delay}ms...")
                time.sleep(wait_delay / 1000.0)
                
                # 刷新截图 - 添加延迟确保缓存更新
                context.tasker.controller.post_screencap().wait()
                time.sleep(0.1)  # 等待控制器缓存更新
                
                return True
                
            except Exception as e:
                logger.error(f"  尝试 {attempt}/{retry_times} [X] 点击'确定'失败: {e}", exc_info=True)
                if attempt < retry_times:
                    time.sleep(retry_interval / 1000.0)
                else:
                    return False
        
        return False
    
    # _save_debug_screenshot 已移除
