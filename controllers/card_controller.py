from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.card import Card, card_schema, cards_schema
from controllers.comment_controller import comments_bp

cards_bp = Blueprint("cards", __name__, url_prefix="/cards")
cards_bp.register_blueprint(comments_bp)

# /cards - GET - fetch all cards
# /cards/<id> - GET - fetch a specific card
# /cards - POST - create a new card
# /cards/<id> - DELETE - delete a card
# /cards/<id> - PUT, PATCH - edit a card entry

# /cards - GET - fetch all cards
@cards_bp.route("/")
def get_all_cards():
    stmt = db.select(Card).order_by(Card.date.desc())
    cards = db.session.scalars(stmt)
    return cards_schema.dump(cards)

# /cards/<id> - GET - fetch a specific card
@cards_bp.route("/<int:card_id>")
def get_a_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    # stmt = db.select(Card).where(Card.id==card_id)
    card = db.session.scalar(stmt)
    if card:
        return card_schema.dump(card)
    else:
        return {"error": f"Card with id '{card_id}' not found"}, 404
    
# /cards - POST - create a new card
@cards_bp.route("/", methods=["POST"])
@jwt_required()
def create_card():
    # get the data from the body of the request
    body_data = card_schema.load(request.get_json())
    # create a new card model instance
    card = Card(
        title = body_data.get("title"),
        description = body_data.get("description"),
        date = date.today(),
        status = body_data.get("status"),
        priority = body_data.get("priority"),
        user_id = get_jwt_identity()
    )
    # add and commit to the DB
    db.session.add(card)
    db.session.commit()
    # response message
    return card_schema.dump(card)

# /cards/<id> - DELETE - delete a card
@cards_bp.route("/<int:card_id>", methods=["DELETE"])
@jwt_required()
def delete_card(card_id):
    # fetch the card from the database
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    # if card exists
    if card:
        # delete the card
        db.session.delete(card)
        db.session.commit()
        return {"message": f"Card {card.title} deleted successfully!"}
    # else
    else:
        # return error message
        return {"error": f"Card with id {card_id} not found"}, 404

# /cards/<id> - PUT, PATCH - edit a card entry
@cards_bp.route("/<int:card_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_card(card_id):
    # get the info from the body of the request
    body_data = card_schema.load(request.get_json(), partial=True)
    # get the card from the database
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    # if the card exists
    if card:
        # update the fields as required
        card.title = body_data.get("title") or card.title
        card.description = body_data.get("description") or card.description
        card.status = body_data.get("status") or card.status
        card.priority = body_data.get("priority") or card.priority
        # commit to the DB
        db.session.commit()
        # return acknowledgement
        return card_schema.dump(card)
    # else
    else:
        # return error message
        return {"error": f"Card with id {card_id} not found."}, 404