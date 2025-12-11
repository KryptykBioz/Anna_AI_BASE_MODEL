# ============================================================================
# FILE: BASE/core/cognitive_loop_manager.py
# FIXED: Continuous thinking without pauses after responses
# ============================================================================

"""
Cognitive Loop Manager - Continuous Autonomous Thinking
Manages background cognitive loop that runs independently of user input
FIXED: Response generation does NOT interrupt continuous thinking
"""

import asyncio
import time
from typing import Optional
from BASE.core.logger import Logger


class CognitiveLoopManager:
    """
    Manages continuous autonomous thinking loop
    Ensures agent is always cognitively active
    """
    
    def __init__(self, thought_processor, controls, logger: Logger):
        """
        Initialize cognitive loop manager
        
        Args:
            thought_processor: ThoughtProcessor instance
            controls: Controls module
            logger: Logger instance
        """
        self.thought_processor = thought_processor
        self.controls = controls
        self.logger = logger
        
        self.is_running = False
        self.loop_task = None
        self.loop_interval = 0.1  # FIXED: Fast checking (100ms)
        
        # Statistics
        self.total_cycles = 0
        self.reactive_cycles = 0
        self.proactive_cycles = 0
        self.idle_cycles = 0
        self.last_stats_log = time.time()
        
        # Response rate limiting (separate from thinking)
        self.last_response_time = 0.0
        self.min_response_interval = 30.0  # Default: 30s between responses
        
        # Callback for autonomous responses (injected by GUI)
        self.autonomous_response_callback = None
    
    async def start_continuous_loop(self):
        """Start the continuous cognitive loop"""
        if self.is_running:
            self.logger.warning("[Cognitive Loop] Already running")
            return
        
        self.is_running = True
        self.logger.system("[Cognitive Loop] [SUCCESS] Starting continuous thinking loop")
        
        # Update response interval based on controls
        limit_processing = getattr(self.controls, 'LIMIT_PROCESSING', False)
        if limit_processing:
            delay = getattr(self.controls, 'DELAY_TIMER', 30)
            self.min_response_interval = delay
            self.logger.system(
                f"[Cognitive Loop] Response rate limiting: 1 per {delay}s "
                f"(thinking continues unrestricted)"
            )
        else:
            self.min_response_interval = 30.0
            self.logger.system(
                "[Cognitive Loop] No response rate limiting - natural timing"
            )
        
        self.loop_task = asyncio.create_task(self._cognitive_loop())
    
    async def stop_continuous_loop(self):
        """Stop the cognitive loop gracefully"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.system("[Cognitive Loop] Stopping...")
        
        if self.loop_task:
            self.loop_task.cancel()
            try:
                await self.loop_task
            except asyncio.CancelledError:
                pass
        
        self.logger.system("[Cognitive Loop] Stopped")
    
    async def _cognitive_loop(self):
        """
        FIXED: Continuous cognitive stream with no thinking delays
        Thinking happens as fast as possible
        Only response generation is rate-limited
        CRITICAL FIX: Response generation does NOT block thinking
        """
        self.logger.system("[Cognitive Loop] Starting with continuous thinking mode")
        
        while self.is_running:
            try:
                # Kill command check (event-driven, very fast)
                if self.thought_processor.thought_buffer.is_shutdown_requested():
                    self.logger.system("[Cognitive Loop] Kill command detected - STOPPING")
                    self.is_running = False
                    break
                
                if hasattr(self, 'ai_core_ref') and self.ai_core_ref:
                    if self.ai_core_ref.shutdown_flag.is_set():
                        self.logger.system("[Cognitive Loop] AI Core shutdown - STOPPING")
                        self.is_running = False
                        break
                
                self.total_cycles += 1
                
                # Get context (fast operation)
                context_parts = await self.thought_processor.thinking_modes.build_thought_context()
                
                # ================================================================
                # CORE FIX: Process thoughts ALWAYS (no delays here)
                # ================================================================
                processing_occurred = await self.thought_processor.process_thoughts(
                    context_parts=context_parts
                )
                
                if processing_occurred:
                    # Track cycle type
                    if self.thought_processor.thought_buffer.get_unprocessed_events():
                        self.reactive_cycles += 1
                        cycle_type = "reactive"
                    else:
                        self.proactive_cycles += 1
                        cycle_type = "proactive"
                    
                    stats = self.thought_processor.thought_buffer.get_thinking_stats()
                    buffer = self.thought_processor.thought_buffer
                    time_since_user = buffer.get_time_since_last_user_input()
                    
                    self.logger.thinking(
                        f"[Loop] Cycle {self.total_cycles} ({cycle_type}) | "
                        f"Stream: {stats['consecutive_proactive']} | "
                        f"Momentum: {stats['momentum']:.2f} | "
                        f"Last input: {time_since_user:.0f}s ago"
                    )
                else:
                    self.idle_cycles += 1
                    self.thought_processor.thought_buffer.decay_momentum()
                
                # ================================================================
                # CRITICAL FIX: Response check PARALLEL to thinking
                # This runs WITHOUT blocking the thinking loop
                # ================================================================
                asyncio.create_task(self._check_and_generate_response())
                
                # ================================================================
                # ADAPTIVE PACING: Only slow down when truly idle
                # ================================================================
                time_since_user = self.thought_processor.thought_buffer.get_time_since_last_user_input()
                
                if time_since_user < 600:  # Less than 10 minutes
                    # ACTIVE MODE: Think as fast as possible
                    if processing_occurred:
                        # Just processed something - keep going immediately
                        await asyncio.sleep(0.05)  # Minimal yield (50ms)
                    else:
                        # Nothing to process - short pause before checking again
                        await asyncio.sleep(0.2)  # 200ms
                else:
                    # IDLE MODE: After 10+ minutes, slow down slightly
                    if processing_occurred:
                        await asyncio.sleep(0.5)  # 500ms between thoughts
                    else:
                        await asyncio.sleep(2.0)  # 2s when truly idle
                
                # ================================================================
                # Periodic stats (doesn't block anything)
                # ================================================================
                if time.time() - self.last_stats_log > 120.0:
                    self._log_statistics()
                    self.last_stats_log = time.time()
            
            except asyncio.CancelledError:
                self.logger.system("[Cognitive Loop] Cancelled - stopping")
                break
            except Exception as e:
                self.logger.error(f"[Cognitive Loop] Error: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(1.0)
        
        self.logger.system("[Cognitive Loop] STOPPED")

    async def _check_and_generate_response(self):
        """
        FIXED: Check if agent should generate spoken response
        Runs in PARALLEL with thinking loop (non-blocking)
        Rate-limited separately from thinking
        """
        thought_buffer = self.thought_processor.thought_buffer
        
        # Check if should speak
        should_speak, reason, urgency = thought_buffer.should_speak()
        
        if not should_speak:
            return
        
        # ================================================================
        # RATE LIMITING: Only limit RESPONSES, not thinking
        # ================================================================
        time_since_last_response = time.time() - self.last_response_time
        
        # Check if we should respect rate limiting
        limit_processing = getattr(self.controls, 'LIMIT_PROCESSING', False)
        
        if limit_processing:
            if time_since_last_response < self.min_response_interval:
                # Too soon for another response - skip (but thinking continues)
                if getattr(self.controls, 'LOG_RESPONSE_PROCESSING', False):
                    remaining = self.min_response_interval - time_since_last_response
                    self.logger.system(
                        f"[Response] Rate limited - {remaining:.0f}s until next response "
                        f"(thinking continues)"
                    )
                return
        
        # Get AI core reference
        if not hasattr(self, 'ai_core_ref'):
            self.logger.warning("[Response] No AI core reference - cannot generate response")
            return
        
        try:
            # chat_stats = thought_buffer.get_chat_engagement_stats()
            # self.logger.system(
            #     f"[Response Trigger] {reason} (urgency={urgency}) | "
            #     f"Chat: {chat_stats.get('unengaged_count', 0)} unengaged"
            # )
        
            # Generate response through AI core (async, non-blocking)
            response = await self.ai_core_ref.process_user_message(
                message="",  # Empty = autonomous response
                source="AUTONOMOUS_CHAT",
                user_id="system",
                is_image_message=False,
                image_path=None,
                timestamp=time.time(),
                username_override=None
            )
            
            if response:
                self.logger.system(f"[Response Generated] {response}")
                
                # Use callback to queue for GUI (if registered)
                if self.autonomous_response_callback:
                    self.autonomous_response_callback(response)
                else:
                    self.logger.warning("[Response] No callback registered")
                
                # CRITICAL FIX: Update response time but DON'T affect thinking
                self.last_response_time = time.time()
                
                # CRITICAL FIX: Don't reset momentum - keep thinking active
                # The thought buffer maintains its momentum naturally
            
        except Exception as e:
            self.logger.error(f"[Response Generation] Error: {e}")
            import traceback
            traceback.print_exc()

    def set_ai_core(self, ai_core):
        """
        Inject AI core reference for response generation
        
        Args:
            ai_core: AICore instance
        """
        self.ai_core_ref = ai_core
    
    def _log_statistics(self):
        """Log cognitive loop statistics"""
        total = self.total_cycles
        reactive = self.reactive_cycles
        proactive = self.proactive_cycles
        idle = self.idle_cycles
        
        if total == 0:
            return
        
        reactive_pct = (reactive / total * 100)
        proactive_pct = (proactive / total * 100)
        idle_pct = (idle / total * 100)
        
        self.logger.system(
            f"[Loop Stats] Total: {total} | "
            f"Reactive: {reactive} ({reactive_pct:.1f}%) | "
            f"Proactive: {proactive} ({proactive_pct:.1f}%) | "
            f"Idle: {idle} ({idle_pct:.1f}%)"
        )
    
    def get_statistics(self) -> dict:
        """Get current statistics as dict"""
        return {
            'total_cycles': self.total_cycles,
            'reactive_cycles': self.reactive_cycles,
            'proactive_cycles': self.proactive_cycles,
            'idle_cycles': self.idle_cycles,
            'is_running': self.is_running,
            'last_response_time': self.last_response_time,
            'min_response_interval': self.min_response_interval
        }