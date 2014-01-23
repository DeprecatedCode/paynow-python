# PayNow Models

from flask import session
import string
import random
from datetime import datetime
from mongoengine import Document, StringField, ReferenceField, \
                        BooleanField, DecimalField, DateTimeField, \
                        IntField

class BaseDocument(Document):
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'abstract': True
    }

    @classmethod
    def create(cls, **kwargs):
        model = cls(**kwargs)
        model.save()
        return model

    def update(self, **kwargs):
        for field in kwargs.keys():

            if field == 'created_at':
                continue

            self[field] = kwargs[field]

        self['updated_at'] = datetime.now()
        self.save()


class User(BaseDocument):

    name = StringField()
    phone = StringField()
    email = StringField()

    default_payment_method = ReferenceField('PaymentMethod')

    @property
    def json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "phone": self.phone,
            "email": self.email
        }


class PaymentMethod(BaseDocument):

    user = ReferenceField(User, required=True)
    type = StringField(choices=['credit_card'], required=True)
    color = StringField()
    name = StringField()

    billing_name = StringField(required=True)
    billing_expires = StringField(required=True)
    billing_zip = StringField(required=True)

    card_type = StringField(required=True)
    last4 = StringField()

    stripe_card_token = StringField()

    @property
    def json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.type,
            "color": self.color,
            "billing_name": self.billing_name,
            "billing_expires": self.billing_expires,
            "billing_zip": self.billing_zip,
            "last4": self.last4,
            "card_type": self.card_type
        }

    @classmethod
    def add(cls, **kwargs):

        if 'card_number' not in kwargs:
            raise ValueError('Card number not given')

        card_number = kwargs['card_number']
        kwargs.pop('card_number')

        if len(card_number) < 12 or len(card_number) > 19:
            raise ValueError('Card number not valid')

        # Auto-determine card type
        if card_number.startswith('34') or card_number.startswith('37'):
            kwargs['card_type'] = 'AMEX'

        elif card_number.startswith('5'):
            kwargs['card_type'] = 'MasterCard'

        elif card_number.startswith('4'):
            kwargs['card_type'] = 'VISA'

        else:
            kwargs['card_type'] = 'Credit Card'

        kwargs['last4'] = card_number[-4:]

        return cls.create(**kwargs)


class Payment(BaseDocument):

    code_chars = string.uppercase + string.digits

    code = StringField(required=True)
    user = ReferenceField(User, required=True)
    completed = BooleanField(default=False, required=True)

    amount = DecimalField(default=0, required=True)
    tip_amount = DecimalField()
    total_amount = DecimalField(default=0, required=True)

    tip_percentage = IntField(default=0, required=True)

    payment_method = ReferenceField(PaymentMethod, required=True)

    stripe_token = StringField()
    stripe_payment_status = StringField()

    @property
    def json(self):
        data = {
            "id": str(self.id),
            "code": self.code,
            "user": self.user.json,
            "completed": self.completed,
            "amount": self.amount,
            "tip_amount": self.tip_amount
        }

        if session.user == self.user:
            data["payment_method"] = self.payment_method.json

        return data

    @classmethod
    def generate(cls, **kwargs):
        code = random.choice(string.uppercase) + \
               random.choice(string.digits) + \
               random.choice(string.digits) + \
               random.choice(string.uppercase)
        return cls.create(code=code, **kwargs)

