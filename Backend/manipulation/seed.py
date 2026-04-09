from manipulation.database import SessionLocal, engine
from manipulation.models import Base, Source
import datetime

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    try:
        # Check if empty
        if not db.query(Source).first():
            # Seed a sample source to verify database models
            sample_source = Source(
                source_key="0xabc123",
                source_type="wallet",
                display_name="Demo Wallet"
            )
            db.add(sample_source)
            db.commit()
            print("Database seeded with sample source.")
        else:
            print("Database already contains data.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
