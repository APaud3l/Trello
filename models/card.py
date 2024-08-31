from init import db, ma
from marshmallow import fields, validates
from marshmallow.validate import Length, And, Regexp, OneOf
from marshmallow.exceptions import ValidationError

VALID_STATUSES = ("To Do", "In Progress", "Completed", "Testing", "Deployed")
VALID_PRIORITIES = ("Low", "Medium", "High", "Immediate")

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    status = db.Column(db.String)
    priority = db.Column(db.String)
    date = db.Column(db.Date) # Created Date

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)

    user = db.relationship('User', back_populates='cards')
    comments = db.relationship('Comment', back_populates='card', cascade="all, delete")


class CardSchema(ma.Schema):
    user = fields.Nested('UserSchema', only=["id", "name", "email"])
    comments = fields.List(fields.Nested('CommentSchema', exclude=['card']))

    title = fields.String(required=True, validate=And(Length(min=4, error="Title must be at least 4 characters in length."), Regexp("^[A-Z][A-Za-z0-9 ]+$", error="Title must start with a capital letter and have alphanumeric characters only.")))

    status = fields.String(validate=OneOf(VALID_STATUSES))

    priority = fields.String(validate=OneOf(VALID_PRIORITIES, error="Invalid Priority Selected."))

    @validates("status")
    def validate_status(self, value):
        # if trying to see the value of status as "In Progress"
        if value == VALID_STATUSES[1]:
            # check whether an existing In Progress card exists or not
            # SELECT COUNT(*) FROM table_name WHERE status="In Progress"
            stmt = db.select(db.func.count()).select_from(Card).filter_by(status=VALID_STATUSES[1])
            count = db.session.scalar(stmt)
            # if it exists
            if count > 0:
                # send error message
                raise ValidationError("You already have an In-Progress card.")
                          
    class Meta:
        fields = ("id", "title", "description", "status", "priority", "date", "user", "comments")
        ordered = True

card_schema = CardSchema()
cards_schema = CardSchema(many=True)

