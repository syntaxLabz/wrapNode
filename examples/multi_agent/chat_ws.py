from agent_api_framework import AgentWSHandler
from fastapi import WebSocket
import json
import time
import asyncio
import random


class ChatWSHandler(AgentWSHandler):
    """
    AI chat handler that simulates an intelligent conversation agent.
    """
    
    def __init__(self):
        self.conversation_history = []
        self.ai_responses = [
            "That's a fascinating perspective! Tell me more about your thoughts on this.",
            "I understand what you're saying. Have you considered the implications of that approach?",
            "Your idea has merit. Let me think about how we could expand on that concept.",
            "That's an interesting point. How do you think this relates to current trends?",
            "I appreciate your insight. What led you to that conclusion?",
            "That's a creative way to look at it. What would be the next steps?",
            "I can see the potential in your thinking. What challenges might we face?",
            "Your approach is innovative. How would you measure success?",
            "That's a thoughtful analysis. What alternatives have you considered?",
            "I'm intrigued by your perspective. Can you elaborate on the key benefits?"
        ]
    
    async def handle(self, websocket: WebSocket):
        try:
            # Send welcome message
            welcome_msg = {
                "type": "agent",
                "message": "Hello! I'm your AI assistant. I'm here to help you explore ideas and have meaningful conversations. What's on your mind today?",
                "timestamp": time.time(),
                "category": "tech"
            }
            await websocket.send_text(json.dumps(welcome_msg))
            
            while True:
                message = await websocket.receive_text()
                
                try:
                    data = json.loads(message)
                    user_message = data.get("message", "")
                    category = data.get("category", "tech")
                except json.JSONDecodeError:
                    user_message = message
                    category = "tech"
                
                if not user_message.strip():
                    continue
                
                # Store conversation history
                self.conversation_history.append({
                    "sender": "user",
                    "message": user_message,
                    "timestamp": time.time(),
                    "category": category
                })
                
                # Simulate thinking time
                thinking_msg = {
                    "type": "thinking",
                    "message": "Agent is thinking...",
                    "timestamp": time.time()
                }
                await websocket.send_text(json.dumps(thinking_msg))
                
                # Simulate processing delay
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
                # Generate AI response
                ai_response = self._generate_response(user_message, category)
                
                # Store AI response in history
                self.conversation_history.append({
                    "sender": "agent",
                    "message": ai_response,
                    "timestamp": time.time(),
                    "category": category
                })
                
                # Send AI response
                response_msg = {
                    "type": "agent",
                    "message": ai_response,
                    "timestamp": time.time(),
                    "category": category
                }
                await websocket.send_text(json.dumps(response_msg))
                
        except Exception as e:
            print(f"Chat WebSocket error: {e}")
    
    def _generate_response(self, user_message: str, category: str) -> str:
        """
        Generate an AI response based on the user message and category.
        """
        # Simple keyword-based response generation
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! It's great to connect with you. What exciting ideas are you working on today?"
        
        elif any(word in message_lower for word in ["help", "assist", "support"]):
            return "I'm here to help! Whether you need brainstorming, problem-solving, or just want to explore ideas, I'm ready to collaborate. What specific area would you like to focus on?"
        
        elif category == "tech" and any(word in message_lower for word in ["ai", "artificial intelligence", "machine learning", "technology"]):
            return "AI and technology are fascinating fields! The rapid advancement in machine learning is opening up incredible possibilities. What specific aspect of AI interests you most? Are you thinking about applications, ethics, or perhaps the technical implementation?"
        
        elif category == "creative" and any(word in message_lower for word in ["art", "design", "creative", "innovation"]):
            return "Creativity is such a powerful force for innovation! I love how creative thinking can transform problems into opportunities. What creative project or challenge are you working on? I'd be excited to help you explore new angles and possibilities."
        
        elif category == "business" and any(word in message_lower for word in ["business", "startup", "entrepreneur", "market"]):
            return "The business world is full of exciting opportunities! Whether you're building a startup, exploring new markets, or optimizing operations, there's always room for innovative thinking. What business challenge or opportunity are you most excited about right now?"
        
        else:
            # Fallback to random response
            return random.choice(self.ai_responses)
    
    async def on_connect(self, websocket: WebSocket) -> bool:
        print("Chat WebSocket connection requested")
        return True
    
    async def on_disconnect(self, websocket: WebSocket, close_code: int):
        print(f"Chat WebSocket disconnected with code: {close_code}")
        print(f"Conversation had {len(self.conversation_history)} messages")