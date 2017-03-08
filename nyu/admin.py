from django.contrib.admin import AdminSite
from django.shortcuts import render
from django.conf.urls import url
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from otcore.hit.models import Hit, Basket, Scope
from otcore.hit.admin import HitAdmin, BasketAdmin, ScopeAdmin

from otcore.lex.models import StopWord, Acronym, Expression, Irregular
from otcore.lex.admin import StopWordAdmin, AcronymAdmin, ExpressionAdmin, IrregularAdmin

from otcore.occurrence.models import Location, Document, Occurrence, Content
from otcore.occurrence.admin import DocTypeAdmin, LocationAdmin, DocumentAdmin, OccurrenceAdmin, ContentAdmin

from otcore.relation.models import RelatedBasket, RelationType, RelatedHit
from otcore.relation.admin import RelatedBasketAdmin

from otcore.topic.models import Tokengroup, Ttype
from otcore.topic.admin import TokengroupAdmin, TtypeAdmin


class NYUAdmin(AdminSite):
    site_header = getattr(settings, 'MEDUSA_ADMIN_HEADER', 'NYU - Enhanced Networked Monographs')
    site_url = getattr(settings, 'MEDUSA_ADMIN_SITE_URL', '')


nyu_admin = NYUAdmin(name='nyu_admin')

nyu_admin.register(User, UserAdmin)
nyu_admin.register(Group, GroupAdmin)
nyu_admin.register(Hit, HitAdmin)
nyu_admin.register(Basket, BasketAdmin)
nyu_admin.register(Scope, ScopeAdmin)
nyu_admin.register(StopWord, StopWordAdmin)
nyu_admin.register(Acronym, AcronymAdmin)
nyu_admin.register(Expression, ExpressionAdmin)
nyu_admin.register(Irregular, IrregularAdmin)
nyu_admin.register(Location, LocationAdmin)
nyu_admin.register(Document, DocumentAdmin)
nyu_admin.register(Occurrence, OccurrenceAdmin)
nyu_admin.register(Content, ContentAdmin)
nyu_admin.register(RelatedBasket, RelatedBasketAdmin)
nyu_admin.register(Tokengroup, TokengroupAdmin)
nyu_admin.register(Ttype, TtypeAdmin)
