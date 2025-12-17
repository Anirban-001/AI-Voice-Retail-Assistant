"""
Base Agent class for Agentic AI Retail System
All specialized agents inherit from this base class
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from services.llm_service import LLMService
from services.database import DatabaseService


class AgentType(Enum):
    """Types of agents in the system"""
    ORCHESTRATOR = "orchestrator"
    RECOMMENDATION = "recommendation"
    INVENTORY = "inventory"
    PAYMENT = "payment"


@dataclass
class AgentMessage:
    """Standard message format for inter-agent communication"""
    message_id: str
    from_agent: AgentType
    to_agent: AgentType
    intent: str
    payload: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent.value,
            "to_agent": self.to_agent.value,
            "intent": self.intent,
            "payload": self.payload,
            "context": self.context,
            "timestamp": self.timestamp
        }


@dataclass
class AgentResponse:
    """Standard response format from agents"""
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    suggested_actions: List[str] = field(default_factory=list)
    next_agent: Optional[AgentType] = None
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "suggested_actions": self.suggested_actions,
            "next_agent": self.next_agent.value if self.next_agent else None
        }


class BaseAgent(ABC):
    """
    Base class for all agents in the system
    
    Provides:
    - Common logging
    - LLM service access
    - Database service access
    - Standard message handling
    - Context management
    """
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"agent.{agent_type.value}")
        self.llm = LLMService
        self.db = DatabaseService
        
        # Agent-specific system prompt
        self.system_prompt = self._get_system_prompt()
        
        self.logger.info(f"{agent_type.value} agent initialized")
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process an incoming message and return a response
        
        Args:
            message: The incoming AgentMessage
        
        Returns:
            AgentResponse with results
        """
        pass
    
    def get_context_summary(self, context: Dict) -> str:
        """Generate a text summary of the current context"""
        return f"""
Session Context:
- Language: {context.get('language', 'en')}
- Mood: {context.get('mood', 'neutral')} ({context.get('mood_confidence', 0):.0%} confidence)
- Cart Items: {len(context.get('cart', []))}
- User ID: {context.get('user_id', 'anonymous')}
- Channel: {context.get('channel', 'web')}
"""
    
    def generate_response(
        self,
        user_message: str,
        context: Dict,
        additional_context: str = ""
    ) -> str:
        """Generate a response using the LLM"""
        
        full_prompt = self.system_prompt
        if additional_context:
            full_prompt += f"\n\nAdditional Context:\n{additional_context}"
        
        return self.llm.generate_response(
            user_message=user_message,
            context=context,
            agent_type=self.agent_type.value,
            system_prompt=full_prompt,
            conversation_history=context.get("conversation_history", [])
        )
    
    def log_action(self, action: str, details: Dict = None):
        """Log an agent action"""
        self.logger.info(f"[{self.agent_type.value}] {action}")
        if details:
            self.logger.debug(f"Details: {details}")
    
    def create_handoff_message(
        self,
        to_agent: AgentType,
        intent: str,
        payload: Dict,
        context: Dict
    ) -> AgentMessage:
        """Create a message to hand off to another agent"""
        import uuid
        
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            from_agent=self.agent_type,
            to_agent=to_agent,
            intent=intent,
            payload=payload,
            context=context
        )


class AgentRegistry:
    """
    Registry for managing all agents
    Allows dynamic agent lookup and routing
    """
    
    _agents: Dict[AgentType, BaseAgent] = {}
    
    @classmethod
    def register(cls, agent: BaseAgent):
        """Register an agent"""
        cls._agents[agent.agent_type] = agent
        logging.info(f"Registered agent: {agent.agent_type.value}")
    
    @classmethod
    def get(cls, agent_type: AgentType) -> Optional[BaseAgent]:
        """Get an agent by type"""
        return cls._agents.get(agent_type)
    
    @classmethod
    def get_all(cls) -> Dict[AgentType, BaseAgent]:
        """Get all registered agents"""
        return cls._agents
    
    @classmethod
    async def route_message(cls, message: AgentMessage) -> AgentResponse:
        """Route a message to the appropriate agent"""
        agent = cls.get(message.to_agent)
        
        if not agent:
            return AgentResponse(
                success=False,
                message=f"Agent {message.to_agent.value} not found"
            )
        
        return await agent.process(message)
