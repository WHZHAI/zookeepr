<br />
<ul id="usermenu" class="menu">

% if 'signed_in_person_id' in session:

<li>
signed in
# as <% c.signed_in_person.email_address %>
</li>

<li>
<% h.link_to('my home', url=h.url('home')) %>
</li>

#<li><% h.link_to('my profile', url=h.url(controller='person', action='view', id=session['person_id'])) %></li>

<li>
<% h.link_to('sign out', url=h.url(controller='account', action='signout', id=None)) %>
</li>

% else:

<li>
<% h.link_to('sign in', url=h.url(controller='account', action='signin', id=None)) %>
</li>

<li>
<% h.link_to('new user?', url=h.url(controller='account', action='new', id=None)) %>
</li>

% #endif
</ul>