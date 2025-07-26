"""
Tests for WebSocket functionality

Tests the real-time features including:
- WebSocket connections
- Real-time messaging
- Collaborative editing
- Chat functionality
- Status updates
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from app.main import app
from app.models.auth import UserModel, UserRole
from app.core.websocket_manager import websocket_manager, ConnectionType, MessageType
from app.services.realtime_service import realtime_service
from app.services.chat_service import chat_service, ChatType
from app.services.collaboration_service import collaboration_service
from app.services.status_service import status_service, StatusType, StatusLevel


class TestWebSocketManager:
    """Test WebSocket manager functionality"""
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user"""
        return UserModel(
            id="user123",
            email="test@example.com",
            name="Test User",
            role=UserRoleEnum.DOCTOR,
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket"""
        websocket = Mock(spec=WebSocket)
        websocket.accept = AsyncMock()
        websocket.send_json = AsyncMock()
        websocket.close = AsyncMock()
        websocket.receive_json = AsyncMock()
        return websocket
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, mock_websocket, mock_user):
        """Test basic WebSocket connection"""
        connection_id = "test_connection_123"
        
        # Test connection
        connection = await websocket_manager.connect(
            websocket=mock_websocket,
            connection_id=connection_id,
            user=mock_user,
            connection_type=ConnectionType.ENCOUNTER,
            resource_id="encounter_123"
        )
        
        assert connection is not None
        assert connection.connection_id == connection_id
        assert connection.user.id == mock_user.id
        assert connection.connection_type == ConnectionType.ENCOUNTER
        assert connection.resource_id == "encounter_123"
        assert connection.is_active is True
        
        # Verify connection is stored
        assert connection_id in websocket_manager.connections
        assert "encounter_123" in websocket_manager.resource_connections
        assert mock_user.id in websocket_manager.user_connections
        
        # Test disconnection
        await websocket_manager.disconnect(connection_id)
        
        assert connection_id not in websocket_manager.connections
        assert "encounter_123" not in websocket_manager.resource_connections
        assert mock_user.id not in websocket_manager.user_connections
    
    @pytest.mark.asyncio
    async def test_message_broadcasting(self, mock_websocket, mock_user):
        """Test message broadcasting to connections"""
        connection_id = "test_connection_123"
        resource_id = "encounter_123"
        
        # Connect WebSocket
        await websocket_manager.connect(
            websocket=mock_websocket,
            connection_id=connection_id,
            user=mock_user,
            connection_type=ConnectionType.ENCOUNTER,
            resource_id=resource_id
        )
        
        # Test broadcasting to resource
        test_message = {
            "type": MessageType.ENCOUNTER_UPDATE.value,
            "data": {"test": "data"}
        }
        
        sent_count = await websocket_manager.broadcast_to_resource(
            resource_id, test_message
        )
        
        assert sent_count == 1
        mock_websocket.send_json.assert_called_once()
        
        # Cleanup
        await websocket_manager.disconnect(connection_id)
    
    @pytest.mark.asyncio
    async def test_auto_save_functionality(self, mock_websocket, mock_user):
        """Test auto-save functionality"""
        connection_id = "test_connection_123"
        encounter_id = "encounter_123"
        
        # Connect WebSocket
        await websocket_manager.connect(
            websocket=mock_websocket,
            connection_id=connection_id,
            user=mock_user,
            connection_type=ConnectionType.ENCOUNTER,
            resource_id=encounter_id
        )
        
        # Start auto-save
        await websocket_manager.start_auto_save(encounter_id, interval_seconds=1)
        
        # Wait for auto-save trigger
        await asyncio.sleep(1.5)
        
        # Verify auto-save message was sent
        assert mock_websocket.send_json.call_count >= 1
        
        # Cleanup
        await websocket_manager.disconnect(connection_id)
    
    @pytest.mark.asyncio
    async def test_connection_stats(self, mock_websocket, mock_user):
        """Test connection statistics"""
        # Initial stats
        stats = websocket_manager.get_connection_stats()
        initial_count = stats["total_connections"]
        
        # Connect WebSocket
        connection_id = "test_connection_123"
        await websocket_manager.connect(
            websocket=mock_websocket,
            connection_id=connection_id,
            user=mock_user,
            connection_type=ConnectionType.ENCOUNTER,
            resource_id="encounter_123"
        )
        
        # Check updated stats
        stats = websocket_manager.get_connection_stats()
        assert stats["total_connections"] == initial_count + 1
        assert stats["connections_by_type"][ConnectionType.ENCOUNTER.value] >= 1
        assert stats["active_resources"] >= 1
        assert stats["connected_users"] >= 1
        
        # Cleanup
        await websocket_manager.disconnect(connection_id)


class TestRealTimeService:
    """Test real-time service functionality"""
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user"""
        return UserModel(
            id="user123",
            email="test@example.com",
            name="Test User",
            role=UserRoleEnum.DOCTOR,
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def sample_encounter_data(self):
        """Create sample encounter data"""
        return {
            "id": "encounter_123",
            "patient_id": "patient_123",
            "soap": {
                "subjective": {"chief_complaint": "Test complaint"},
                "objective": {"vital_signs": "Normal"},
                "assessment": {"diagnosis": "Test diagnosis"},
                "plan": {"treatment": "Test treatment"}
            }
        }
    
    @pytest.mark.asyncio
    async def test_soap_section_update(self, mock_user, sample_encounter_data):
        """Test SOAP section updates with real-time broadcasting"""
        encounter_id = "encounter_123"
        
        with patch.object(websocket_manager, 'broadcast_to_resource') as mock_broadcast:
            # Update SOAP section
            result = await realtime_service.update_soap_section(
                encounter_id=encounter_id,
                section="subjective",
                field="chief_complaint",
                value="Updated complaint",
                user=mock_user,
                broadcast=True
            )
            
            assert result["success"] is True
            assert result["encounter_id"] == encounter_id
            assert result["section"] == "subjective"
            assert result["field"] == "chief_complaint"
            
            # Verify broadcast was called
            mock_broadcast.assert_called_once()
            call_args = mock_broadcast.call_args
            assert call_args[0][0] == encounter_id  # encounter_id
            assert call_args[0][1]["type"] == MessageType.SOAP_UPDATE.value
    
    @pytest.mark.asyncio
    async def test_typing_indicators(self, mock_user):
        """Test typing indicator functionality"""
        encounter_id = "encounter_123"
        
        with patch.object(websocket_manager, 'broadcast_to_resource') as mock_broadcast:
            # Set typing indicator
            success = await realtime_service.set_typing_indicator(
                encounter_id=encounter_id,
                user=mock_user,
                section="subjective",
                is_typing=True
            )
            
            assert success is True
            
            # Verify broadcast was called
            mock_broadcast.assert_called_once()
            call_args = mock_broadcast.call_args
            assert call_args[0][1]["type"] == MessageType.TYPING_START.value
            
            # Get typing indicators
            indicators = await realtime_service.get_typing_indicators(encounter_id)
            assert len(indicators) == 1
            assert indicators[0]["user_id"] == mock_user.id
    
    @pytest.mark.asyncio
    async def test_auto_save_performance(self, mock_user, sample_encounter_data):
        """Test auto-save performance and reliability"""
        encounter_id = "encounter_123"
        
        # Mock encounter service
        with patch('app.services.realtime_service.encounter_service') as mock_encounter_service:
            mock_encounter_service.get_encounter_by_id.return_value = Mock(**sample_encounter_data)
            mock_encounter_service.update_encounter.return_value = Mock(**sample_encounter_data)
            
            # Initialize auto-save state
            realtime_service.auto_save_states[encounter_id] = {
                "last_save": datetime.utcnow(),
                "pending_changes": {
                    "subjective": {
                        "chief_complaint": {
                            "value": "Test complaint",
                            "user_id": mock_user.id,
                            "updated_at": datetime.utcnow().isoformat()
                        }
                    }
                },
                "save_in_progress": False,
                "interval": 30
            }
            
            # Perform auto-save
            result = await realtime_service.perform_auto_save(encounter_id)
            
            assert result["success"] is True
            assert result["encounter_id"] == encounter_id
            assert "saved_at" in result


class TestChatService:
    """Test chat service functionality"""
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user"""
        return UserModel(
            id="user123",
            email="test@example.com",
            name="Test User",
            role=UserRoleEnum.DOCTOR,
            is_active=True,
            is_verified=True
        )
    
    @pytest.mark.asyncio
    async def test_chat_room_creation(self, mock_user):
        """Test chat room creation"""
        result = await chat_service.create_chat_room(
            room_type=ChatType.AI_ASSISTANT,
            creator=mock_user,
            name="Test AI Chat",
            description="Test chat room"
        )
        
        assert result["success"] is True
        assert "room_id" in result
        assert result["room_data"]["type"] == ChatType.AI_ASSISTANT.value
        assert result["room_data"]["creator_id"] == mock_user.id
        
        room_id = result["room_id"]
        assert room_id in chat_service.chat_rooms
    
    @pytest.mark.asyncio
    async def test_chat_message_sending(self, mock_user):
        """Test sending chat messages"""
        # Create chat room first
        room_result = await chat_service.create_chat_room(
            room_type=ChatType.GENERAL,
            creator=mock_user,
            name="Test Chat"
        )
        room_id = room_result["room_id"]
        
        with patch.object(websocket_manager, 'broadcast_to_resource') as mock_broadcast:
            # Send message
            result = await chat_service.send_message(
                room_id=room_id,
                sender=mock_user,
                content="Test message",
                message_type="text"
            )
            
            assert result["success"] is True
            assert "message_id" in result
            
            # Verify broadcast was called
            mock_broadcast.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ai_chat_integration(self, mock_user):
        """Test AI chat integration"""
        # Create AI chat room
        room_result = await chat_service.create_chat_room(
            room_type=ChatType.AI_ASSISTANT,
            creator=mock_user,
            name="AI Assistant"
        )
        room_id = room_result["room_id"]
        
        with patch('app.services.chat_service.ai_service') as mock_ai_service:
            mock_ai_service.chat_with_ai.return_value = Mock(
                message="AI response",
                conversation_id="conv_123",
                suggestions=["Suggestion 1", "Suggestion 2"],
                confidence=Mock(value="high")
            )
            
            with patch.object(websocket_manager, 'broadcast_to_resource') as mock_broadcast:
                # Send message to AI
                result = await chat_service.send_message(
                    room_id=room_id,
                    sender=mock_user,
                    content="Hello AI",
                    message_type="text"
                )
                
                assert result["success"] is True
                
                # Wait for AI response
                await asyncio.sleep(0.1)
                
                # Verify AI service was called
                mock_ai_service.chat_with_ai.assert_called_once()


class TestCollaborationService:
    """Test collaboration service functionality"""
    
    @pytest.fixture
    def mock_user1(self):
        """Create mock user 1"""
        return UserModel(
            id="user1",
            email="user1@example.com",
            name="User One",
            role=UserRoleEnum.DOCTOR,
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def mock_user2(self):
        """Create mock user 2"""
        return UserModel(
            id="user2",
            email="user2@example.com",
            name="User Two",
            role=UserRoleEnum.NURSE,
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def sample_document(self):
        """Create sample document for collaboration"""
        return {
            "subjective": {"chief_complaint": "Initial complaint"},
            "objective": {"vital_signs": "Normal"},
            "assessment": {"diagnosis": "Initial diagnosis"},
            "plan": {"treatment": "Initial treatment"}
        }
    
    @pytest.mark.asyncio
    async def test_collaborative_session_creation(self, mock_user1, sample_document):
        """Test creating collaborative session"""
        encounter_id = "encounter_123"
        
        session = await collaboration_service.start_collaborative_session(
            encounter_id=encounter_id,
            user=mock_user1,
            initial_document=sample_document
        )
        
        assert session.encounter_id == encounter_id
        assert mock_user1.id in session.participants
        assert session.document_state == sample_document
        assert session.version == 1
    
    @pytest.mark.asyncio
    async def test_multiple_user_collaboration(self, mock_user1, mock_user2, sample_document):
        """Test multiple users collaborating"""
        encounter_id = "encounter_123"
        
        # User 1 starts session
        session = await collaboration_service.start_collaborative_session(
            encounter_id=encounter_id,
            user=mock_user1,
            initial_document=sample_document
        )
        
        # User 2 joins session
        joined_session = await collaboration_service.join_session(
            encounter_id=encounter_id,
            user=mock_user2
        )
        
        assert len(session.participants) == 2
        assert mock_user1.id in session.participants
        assert mock_user2.id in session.participants
        
        # Test operation application
        operation = {
            "type": "update",
            "section": "subjective",
            "field": "chief_complaint",
            "value": "Updated complaint by user 2"
        }
        
        with patch.object(websocket_manager, 'broadcast_to_resource') as mock_broadcast:
            result = await collaboration_service.apply_operation(
                encounter_id=encounter_id,
                user=mock_user2,
                operation=operation,
                client_version=1
            )
            
            assert result["success"] is True
            assert result["version"] == 2
            
            # Verify broadcast was called
            mock_broadcast.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_section_locking(self, mock_user1, mock_user2, sample_document):
        """Test section locking functionality"""
        encounter_id = "encounter_123"
        
        # Start session with both users
        await collaboration_service.start_collaborative_session(
            encounter_id=encounter_id,
            user=mock_user1,
            initial_document=sample_document
        )
        await collaboration_service.join_session(encounter_id, mock_user2)
        
        # User 1 acquires lock
        success = await collaboration_service.acquire_section_lock(
            encounter_id=encounter_id,
            user=mock_user1,
            section="subjective",
            lock_type="write"
        )
        assert success is True
        
        # User 2 tries to acquire same lock (should fail)
        success = await collaboration_service.acquire_section_lock(
            encounter_id=encounter_id,
            user=mock_user2,
            section="subjective",
            lock_type="write"
        )
        assert success is False
        
        # User 1 releases lock
        success = await collaboration_service.release_section_lock(
            encounter_id=encounter_id,
            user=mock_user1,
            section="subjective"
        )
        assert success is True
        
        # User 2 can now acquire lock
        success = await collaboration_service.acquire_section_lock(
            encounter_id=encounter_id,
            user=mock_user2,
            section="subjective",
            lock_type="write"
        )
        assert success is True


class TestStatusService:
    """Test status service functionality"""
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user"""
        return UserModel(
            id="user123",
            email="test@example.com",
            name="Test User",
            role=UserRoleEnum.DOCTOR,
            is_active=True,
            is_verified=True
        )
    
    @pytest.mark.asyncio
    async def test_notification_creation(self, mock_user):
        """Test creating status notifications"""
        with patch.object(websocket_manager, 'broadcast_notification') as mock_broadcast:
            notification = await status_service.create_notification(
                notification_type=StatusType.SYSTEM,
                level=StatusLevel.INFO,
                title="Test Notification",
                message="This is a test notification",
                broadcast_all=True
            )
            
            assert notification.title == "Test Notification"
            assert notification.level == StatusLevel.INFO
            assert notification.type == StatusType.SYSTEM
            
            # Verify broadcast was called
            mock_broadcast.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_user_presence_management(self, mock_user):
        """Test user presence management"""
        from app.services.status_service import UserStatus
        
        with patch.object(websocket_manager, 'broadcast_notification') as mock_broadcast:
            presence = await status_service.update_user_presence(
                user=mock_user,
                status=UserStatus.ONLINE,
                activity="Working on encounter",
                location="Emergency Department"
            )
            
            assert presence.user_id == mock_user.id
            assert presence.status == UserStatus.ONLINE
            assert presence.current_activity == "Working on encounter"
            assert presence.location == "Emergency Department"
            assert presence.is_available() is True
            
            # Verify broadcast was called
            mock_broadcast.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_medical_alert_creation(self, mock_user):
        """Test medical alert creation"""
        with patch.object(websocket_manager, 'broadcast_notification') as mock_broadcast:
            alert = await status_service.create_medical_alert(
                patient_id="patient_123",
                encounter_id="encounter_123",
                alert_type="High Blood Pressure",
                severity=StatusLevel.WARNING,
                description="Patient blood pressure is 180/110"
            )
            
            assert alert.type == StatusType.MEDICAL_ALERT
            assert alert.level == StatusLevel.WARNING
            assert "High Blood Pressure" in alert.title
            assert alert.metadata["patient_id"] == "patient_123"
            
            # Verify broadcast was called
            mock_broadcast.assert_called_once()
    
    def test_system_status_management(self):
        """Test system status management"""
        initial_status = status_service.get_system_status()
        assert "overall_health" in initial_status
        assert "services" in initial_status
        
        # Update service status
        asyncio.run(status_service.update_system_status("database", "warning", {"issue": "slow queries"}))
        
        updated_status = status_service.get_system_status()
        assert updated_status["services"]["database"] == "warning"


class TestWebSocketPerformance:
    """Test WebSocket performance and load handling"""
    
    @pytest.mark.asyncio
    async def test_multiple_connections_performance(self):
        """Test performance with multiple WebSocket connections"""
        import time
        
        # Create multiple mock connections
        connections = []
        start_time = time.time()
        
        for i in range(100):  # Test with 100 connections
            mock_websocket = Mock(spec=WebSocket)
            mock_websocket.accept = AsyncMock()
            mock_websocket.send_json = AsyncMock()
            mock_websocket.close = AsyncMock()
            
            mock_user = UserModel(
                id=f"user_{i}",
                email=f"user{i}@example.com",
                name=f"User {i}",
                role=UserRoleEnum.DOCTOR,
                is_active=True,
                is_verified=True
            )
            
            connection = await websocket_manager.connect(
                websocket=mock_websocket,
                connection_id=f"connection_{i}",
                user=mock_user,
                connection_type=ConnectionType.ENCOUNTER,
                resource_id="encounter_123"
            )
            connections.append((f"connection_{i}", mock_websocket))
        
        connection_time = time.time() - start_time
        
        # Test broadcasting performance
        start_time = time.time()
        
        test_message = {
            "type": MessageType.ENCOUNTER_UPDATE.value,
            "data": {"test": "performance_data"}
        }
        
        sent_count = await websocket_manager.broadcast_to_resource(
            "encounter_123", test_message
        )
        
        broadcast_time = time.time() - start_time
        
        # Cleanup
        for connection_id, _ in connections:
            await websocket_manager.disconnect(connection_id)
        
        # Performance assertions
        assert connection_time < 5.0  # Should connect 100 users in under 5 seconds
        assert broadcast_time < 1.0   # Should broadcast to 100 users in under 1 second
        assert sent_count == 100      # Should reach all connected users
    
    @pytest.mark.asyncio
    async def test_memory_usage_with_many_messages(self):
        """Test memory usage with high message volume"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create connection
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()
        
        mock_user = UserModel(
            id="test_user",
            email="test@example.com",
            name="Test User",
            role=UserRoleEnum.DOCTOR,
            is_active=True,
            is_verified=True
        )
        
        connection_id = "test_connection"
        await websocket_manager.connect(
            websocket=mock_websocket,
            connection_id=connection_id,
            user=mock_user,
            connection_type=ConnectionType.ENCOUNTER,
            resource_id="encounter_123"
        )
        
        # Send many messages
        for i in range(1000):
            test_message = {
                "type": MessageType.ENCOUNTER_UPDATE.value,
                "data": {"message_id": i, "content": "test_data" * 100}
            }
            await websocket_manager.send_to_connection(connection_id, test_message)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Cleanup
        await websocket_manager.disconnect(connection_id)
        
        # Memory usage should not increase dramatically
        assert memory_increase < 50 * 1024 * 1024  # Less than 50MB increase


if __name__ == "__main__":
    pytest.main([__file__])