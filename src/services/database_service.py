import sqlite3
from typing import Dict, Any
from datetime import datetime
from loguru import logger
import os

class DatabaseService:
    def __init__(self):
        self.db_path = "data/clients.db"
        self._ensure_data_directory()
        self._init_database()
        logger.info("Database service initialized successfully")

    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create clients table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        meeting_date DATE NOT NULL,
                        product_type TEXT NOT NULL,
                        goal TEXT NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create meetings table for tracking client meetings
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS meetings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id INTEGER NOT NULL,
                        meeting_date DATE NOT NULL,
                        meeting_type TEXT NOT NULL,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (client_id) REFERENCES clients (id)
                    )
                """)
                
                conn.commit()
                logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    async def get_all_clients(self) -> list:
        """Get all clients from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, full_name, age, meeting_date, product_type, 
                           goal, description, created_at
                    FROM clients
                    ORDER BY created_at DESC
                """)
                
                clients = []
                for row in cursor.fetchall():
                    clients.append({
                        'id': row[0],
                        'full_name': row[1],
                        'age': row[2],
                        'meeting_date': row[3],
                        'product_type': row[4],
                        'goal': row[5],
                        'description': row[6],
                        'created_at': row[7]
                    })
                return clients
                
        except Exception as e:
            logger.error(f"Error getting all clients: {str(e)}")
            raise

    async def save_client(self, client_data: Dict[str, Any]) -> int:
        """Save client information to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if required fields are present
                required_fields = ['full_name', 'age', 'product_type', 'goal']
                for field in required_fields:
                    if field not in client_data:
                        raise ValueError(f"Missing required field: {field}")
                
                # Set meeting_date to current date if not provided
                if 'meeting_date' not in client_data:
                    client_data['meeting_date'] = datetime.now().strftime('%d.%m.%Y')
                
                # Insert client data
                cursor.execute("""
                    INSERT INTO clients (
                        full_name, age, meeting_date, product_type, 
                        goal, description
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    client_data['full_name'],
                    client_data['age'],
                    datetime.strptime(client_data['meeting_date'], '%d.%m.%Y').date(),
                    client_data['product_type'],
                    client_data['goal'],
                    client_data.get('description', '')
                ))
                
                client_id = cursor.lastrowid
                
                # Insert meeting record
                cursor.execute("""
                    INSERT INTO meetings (
                        client_id, meeting_date, meeting_type, notes
                    ) VALUES (?, ?, ?, ?)
                """, (
                    client_id,
                    datetime.strptime(client_data['meeting_date'], '%d.%m.%Y').date(),
                    client_data.get('meeting_type', 'Initial'),
                    client_data.get('description', '')
                ))
                
                conn.commit()
                logger.info(f"Client information saved successfully. Client ID: {client_id}")
                return client_id
                
        except Exception as e:
            logger.error(f"Error saving client information: {str(e)}")
            raise

    async def get_client(self, client_id: int) -> Dict[str, Any]:
        """Get client information by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, full_name, age, meeting_date, product_type, 
                           goal, description, created_at
                    FROM clients
                    WHERE id = ?
                """, (client_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'full_name': result[1],
                        'age': result[2],
                        'meeting_date': result[3],
                        'product_type': result[4],
                        'goal': result[5],
                        'description': result[6],
                        'created_at': result[7]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting client information: {str(e)}")
            raise

    async def get_client_meetings(self, client_id: int) -> list:
        """Get all meetings for a specific client"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, meeting_date, meeting_type, notes, created_at
                    FROM meetings
                    WHERE client_id = ?
                    ORDER BY meeting_date DESC
                """, (client_id,))
                
                meetings = []
                for row in cursor.fetchall():
                    meetings.append({
                        'id': row[0],
                        'meeting_date': row[1],
                        'meeting_type': row[2],
                        'notes': row[3],
                        'created_at': row[4]
                    })
                return meetings
                
        except Exception as e:
            logger.error(f"Error getting client meetings: {str(e)}")
            raise

# Create singleton instance
database_service = DatabaseService() 