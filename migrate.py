import json
from sqlmodel import SQLModel, Session, select
from main import engine, Board, Column, Bucket, Item

# Load board_data.json
with open('/app/data/doc_0f2fe11fe60c_board_data.json', 'r') as f:
    data = json.load(f)

SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    # Create Board
    board = session.get(Board, 1)
    if not board:
        board = Board(title=data['title'], updated=data['updated'])
        session.add(board)
        session.commit()

    # Create Columns: To Do, In Progress, Completed
    col_map = {}
    col_names = [("To Do", 1), ("In Progress", 2), ("Completed", 3)]
    for col_name, sort_order in col_names:
        col = session.exec(select(Column).where(Column.name == col_name)).first()
        if not col:
            col = Column(board_id=board.id, name=col_name, sort_order=sort_order)
            session.add(col)
            session.commit()
        col_map[col_name] = col.id

    # Map old column types to new columns
    type_to_col = {"active": "To Do", "done": "Completed"}
    
    # Create Buckets and Items
    for col_type, items_list in data['columns'].items():
        target_col_name = type_to_col.get(col_type, "To Do")
        target_col_id = col_map[target_col_name]
        
        for bucket_data in items_list:
            existing_bucket = session.exec(select(Bucket).where(Bucket.name == bucket_data['name'], Bucket.column_id == target_col_id)).first()
            if not existing_bucket:
                existing_bucket = Bucket(column_id=target_col_id, name=bucket_data['name'], sort_order=0)
                session.add(existing_bucket)
                session.commit()
            
            for item in bucket_data['items']:
                # Check if item already exists
                existing_item = session.exec(select(Item).where(Item.text == item['text'], Item.bucket_id == existing_bucket.id)).first()
                if not existing_item:
                    new_item = Item(bucket_id=existing_bucket.id, text=item['text'], done=item['done'], sort_order=0)
                    session.add(new_item)
                    session.commit()

print("Migration complete!")
