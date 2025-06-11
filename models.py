from app import db
from datetime import datetime
from sqlalchemy import desc

class TasaDTF(db.Model):
    __tablename__ = 'tasas_dtf'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(10), nullable=False, unique=True)  # Format: YYYY-MM-DD
    tasa = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TasaDTF {self.fecha}: {self.tasa}%>'
    
    @classmethod
    def get_latest(cls, limit=30):
        """Get the latest DTF rates"""
        return cls.query.order_by(desc(cls.fecha)).limit(limit).all()
    
    @classmethod
    def get_all_ordered(cls):
        """Get all DTF rates ordered by date"""
        return cls.query.order_by(desc(cls.fecha)).all()
    
    @classmethod
    def get_date_range(cls, start_date, end_date):
        """Get DTF rates within a date range"""
        return cls.query.filter(
            cls.fecha >= start_date,
            cls.fecha <= end_date
        ).order_by(desc(cls.fecha)).all()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'fecha': self.fecha,
            'tasa': self.tasa,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
