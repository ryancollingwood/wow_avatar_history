def create_classes(db):
    class AvatarHistory(db.Model):
        __tablename__ = 'avatar_history'

        id = db.Column(db.Integer, primary_key=True)
        level = db.Column(db.Integer)        
        guild = db.Column(db.String(64))
        race = db.Column(db.String(64))
        char_class = db.Column(db.String(64))
        region = db.Column(db.String(256))

        def __repr__(self):
            return f'<AvatarHistory {self.id}>'

    return AvatarHistory
