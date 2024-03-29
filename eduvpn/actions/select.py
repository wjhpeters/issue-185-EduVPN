# python-eduvpn-client - The GNU/Linux eduVPN client and Python API
#
# Copyright: 2017, The Commons Conservancy eduVPN Programme
# SPDX-License-Identifier: GPL-3.0+

import logging
import base64
from eduvpn.util import bytes2pixbuf, get_pixbuf, metadata_of_selected
from eduvpn.config import icon_size
from eduvpn.manager import is_provider_connected
from eduvpn.steps.messages import fetch_messages
from eduvpn.brand import get_brand
import gi
from gi.repository import Gtk
from eduvpn.metadata import Metadata
from typing import Optional

gi.require_version('Gtk', '3.0')
logger = logging.getLogger(__name__)


# ui thread
def select_profile(builder, verifier, lets_connect):  # type: (Gtk.builder, str, bool) -> Optional[Metadata]
    """called when a users selects a configuration"""
    messages_label = builder.get_object('messages-label')
    notebook = builder.get_object('outer-notebook')
    switch = builder.get_object('connect-switch')
    ipv4_label = builder.get_object('ipv4-label')
    ipv6_label = builder.get_object('ipv6-label')

    note_label = builder.get_object('note-label')
    note_label_label = builder.get_object('note-label-label')

    twofa_label = builder.get_object('2fa-label')
    twofa_label_label = builder.get_object('2fa-label-label')
    name_label = builder.get_object('name-label')
    profile_label = builder.get_object('profile-label')
    profile_name_label = builder.get_object('profile-name-label')
    profile_image = builder.get_object('profile-image')
    meta = metadata_of_selected(builder)
    logo, _ = get_brand(lets_connect)

    if not meta:
        logger.info("no configuration selected, showing main logo")
        notebook.set_current_page(0)
        return None
    else:
        logger.info("configuration was selected {} ({})".format(meta.display_name, meta.uuid))
        name_label.set_text(meta.display_name)
        if meta.icon_data:
            icon = bytes2pixbuf(base64.b64decode(meta.icon_data.encode()),
                                width=icon_size['width'] * 2, height=icon_size['height'] * 2)
        else:
            _, icon = get_pixbuf(logo)
        profile_image.set_from_pixbuf(icon)
        profile_label.set_text(meta.connection_type)
        profile_name_label.set_text(meta.profile_display_name)
        connected = is_provider_connected(uuid=meta.uuid)
        switch.set_state(bool(connected))
        if connected:
            ipv4, ipv6 = connected
            ipv4_label.set_text(ipv4)
            ipv6_label.set_text(ipv6)
        else:
            ipv4_label.set_text("-")
            ipv6_label.set_text("-")

        if meta.username:
            twofa_label.set_text(meta.username)
            twofa_label_label.set_text("2FA:")
        else:
            twofa_label.set_text("")
            twofa_label_label.set_text("")

            note_label.set_text("")
            note_label_label.set_text("")

        notebook.show_all()
        notebook.set_current_page(1)

        messages_label.set_markup("")
        if meta.token:
            fetch_messages(meta=meta, builder=builder, verifier=verifier, lets_connect=lets_connect)
        else:
            logger.warning("no token available so not fetching messages")

            messages_label.set_markup("<b><big>Warning</big></b>\nno token available so not fetching messages.")
        return meta
