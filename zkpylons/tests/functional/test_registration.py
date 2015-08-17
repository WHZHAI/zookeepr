import re

from routes import url_for

from zk.model.registration import Registration

from .fixtures import PersonFactory, ProductCategoryFactory, ProductFactory, CeilingFactory
from .utils import do_login


class TestRegistration(object):
    def test_create(self, app, db_session, smtplib):
        data = {
            'person' : {
                'address1' : 'Somewhere',
                'address2' : 'Over the rainbow',
                'city'     : 'Way up high',
                'state'    : 'And the dreams that you dreamed of',
                'postcode' : 'Once in', # a lullaby
                'country'  : 'AUSTRALIA',
                'phone'    : 123456789,
                'mobile'   : 987654321,
                },
            'registration' : {
                'over18'       : '1',
                },
            }


        PersonFactory.reset_sequence()
        ProductCategoryFactory.reset_sequence()
        ProductFactory.reset_sequence()
        CeilingFactory.reset_sequence()


        p = PersonFactory(
                email_address = 'testguy@example.org',
                # Set full set of detail to avoid incomplete profile flag
                firstname = 'Testguy',
                lastname  = 'McTest',
                i_agree   = True,
                activated = True,
                address1  = 'Somewhere',
                city      = 'Over the rainbow',
                postcode  = 'Way up high',
                )

        # Required by templates
        CeilingFactory(name='conference-earlybird')
        CeilingFactory(name='conference-paid')

        ticket_cat = ProductCategoryFactory(name='Ticket', display_mode='accommodation', display='qty', min_qty=0, max_qty=55)
        shirt_cat  = ProductCategoryFactory(name='T-Shirt', display_mode='shirt', display='qty', min_qty=0, max_qty=55)
        dinner_cat = ProductCategoryFactory(name='Penguin Dinner Ticket', display_mode='accommodation', display='qty', min_qty=0, max_qty=55)
        accom_cat  = ProductCategoryFactory(name='Accommodation', display_mode='accommodation', display='qty', min_qty=0, max_qty=55)

        ticket = ProductFactory(category=ticket_cat)
        shirt  = ProductFactory(category=shirt_cat, description="Men's Small")
        dinner = ProductFactory(category=dinner_cat)
        accom  = ProductFactory(category=accom_cat)

        db_session.commit()

        do_login(app, p)
        resp = app.get(url_for(controller='/registration', action='new'))
        resp = resp.maybe_follow()
        f = resp.forms[0]

        for cat in data:
            for elem in data[cat]:
                f[cat+'.'+elem] = data[cat][elem]

        f['products.product_T_Shirt_Mens Small_qty'] = 2
        f['products.product_'+dinner_cat.name+'_'+dinner.description+'_qty'] = 3
        f['products.product_'+ticket_cat.name+'_'+ticket.description+'_qty'] = 4
        f['products.product_'+accom_cat.name+'_'+accom.description+'_qty'] = 5

        resp = f.submit()
        resp = resp.follow() # Failure indicates form validation error

        assert 'Missing value' not in unicode(resp.body, 'utf-8')

        # Test we have an email that is suitable
        assert smtplib.existing is not None
        assert "testguy@example.org" in smtplib.existing.to_addresses


        message = smtplib.existing.message
        assert re.match(r'^.*To:.*testguy@example.org.*', message, re.DOTALL)
        assert re.match(r'^.*Testguy McTest', message, re.DOTALL)
        assert not re.match(r'^.*<!DOCTYPE', message, re.DOTALL) # No HTML

        # test that we have a registration
        pid = p.id
        db_session.expunge_all()

        regs = Registration.find_all()
        assert len(regs) == 1
        assert regs[0].person.id       == pid
        assert regs[0].over18          == (data['registration']['over18'] == '1')
        assert regs[0].person.address1 == data['person']['address1']
        assert regs[0].person.address2 == data['person']['address2']
        assert regs[0].person.city     == data['person']['city']
        assert regs[0].person.state    == data['person']['state']
        assert regs[0].person.postcode == data['person']['postcode']
        assert regs[0].person.country  == data['person']['country']
        assert regs[0].person.phone    == str(data['person']['phone'])
        assert regs[0].person.mobile   == str(data['person']['mobile'])
