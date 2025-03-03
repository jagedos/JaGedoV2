from django.urls import path
from management import (
    views,
    categories,
    brands,
    munits,
    items,
    users,
    counties,
    picks,
    shops,
    products,
    order,
    deliver,
    esettings,
    eaccounts,
    ejobs,
    ecats,
    eskills,
    legald,
    sms,
    roles,
)
from management.items import ProdDataTableView
from management.categories import CatDataTableView, PcatDataTableView
from management.ecats import EcatDataTableView
from management.eskills import EskillsDataTableView
from management.legald import (
    LegalDocumentTypesDataTableView,
    LegalDocumentsDataTableView,
)
from management.products import ProductsListJson
from management.sms import SMSListJson
from management.roles import UsertypesDataTableView
from accounts import reset
from experts.views import (
    getskills,
    getskillsx,
    medit,
    sedit,
    editskill,
    delete,
    tdelete,
)


urlpatterns = [
    path("", views.index, name="index"),
    path("metrics/", views.metrics, name="metrics"),
    path("category/", categories.index, name="cat"),
    path("categories/", CatDataTableView.as_view(), name="category_table"),
    path("storecat/", categories.addrecord, name="storecat"),
    path("catedit/<int:id>", categories.edita, name="catedit"),
    path("updatecat", categories.updaterecord, name="updatecat"),
    path("deletecat/<int:id>", categories.delete, name="deletecat"),
    path("plocator/<int:id>", categories.catitems, name="plocator"),
    path("prod_table/", PcatDataTableView.as_view(), name="prod_table"),
    path("changestat/<int:id>", categories.changestat, name="changestat"),
    path("brand/", brands.index, name="brand"),
    path("storebrand/", brands.addrecord, name="storebrand"),
    path("brandedit/<int:id>", brands.edita, name="brandedit"),
    path("updatebrand", brands.updaterecord, name="updatebrand"),
    path("deletebrand/<int:id>", brands.delete, name="deletebrand"),
    path("unit/", munits.index, name="unit"),
    path("storeunit/", munits.addrecord, name="storeunit"),
    path("unitedit/<int:id>", munits.edita, name="unitedit"),
    path("updateunit", munits.updaterecord, name="updateunit"),
    path("deleteunit/<int:id>", munits.delete, name="deleteunit"),
    path("product/", items.index, name="product"),
    path("products_table/", ProdDataTableView.as_view(), name="products_table"),
    path("storeproduct/", items.addrecord, name="storeproduct"),
    path("productedit/<int:id>", items.edita, name="productedit"),
    path("updateproduct", items.updaterecord, name="updateproduct"),
    path("deleteproduct/<int:id>", items.delete, name="deleteproduct"),
    path("delpimages/<int:id>", items.idelete, name="delpimages"),
    path(
        "update_average_prices/", items.update_all_prices, name="update_average_prices"
    ),
    path("users/", users.index, name="users"),
    path("vusers/", users.vendors, name="vusers"),
    path("pvusers/", users.pvendors, name="pvusers"),
    path("vdocs/<int:id>", users.vdocs, name="vdocs"),
    path("cusers/", users.customers, name="cusers"),
    path("storeuser/", users.addrecord, name="storeuser"),
    path("useredit/<int:id>", users.edita, name="useredit"),
    path("updateuser", users.updaterecord, name="updateuser"),
    path("deleteuser/<int:id>", users.delete, name="deleteuser"),
    path("approveuser/<int:id>", users.uapp, name="approveuser"),
    path("mprofile/", users.profile, name="mprofile"),
    path("update_manager_details/", users.updateprofile, name="update_manager_details"),
    path("initiate_reset/", reset.password_reset_mini, name="initiate_reset"),
    path("vuploadsview/<int:id>", users.vuploads, name="vuploadsview"),
    path("vupsview/<str:id>", users.uviews, name="vupsview"),
    path("county/", counties.index, name="county"),
    path("storecounty/", counties.addrecord, name="storecounty"),
    path("countyedit/<int:id>", counties.edita, name="countyedit"),
    path("updatecounty", counties.updaterecord, name="updatecounty"),
    path("deletecounty/<int:id>", counties.delete, name="deletecounty"),
    path("picks/", picks.index, name="picks"),
    path("storepicks/", picks.addrecord, name="storepicks"),
    path("picksedit/<int:id>", picks.edita, name="picksedit"),
    path("updatepicks", picks.updaterecord, name="updatepicks"),
    path("deletepicks/<int:id>", picks.delete, name="deletepicks"),
    path("vshops/", shops.filter, name="vshops"),
    path("vrshops/", shops.index, name="vrshops"),
    path("vstoreshop/", shops.addrecord, name="vstoreshop"),
    path("vpicksshop/<int:id>", shops.edita, name="vshopedit"),
    path("vupdateshop", shops.updaterecord, name="vupdateshop"),
    path("vdeleteshop/<int:id>", shops.delete, name="vdeleteshop"),
    path("shopstatus/<int:id>", shops.status, name="shopstatus"),
    path("vproducts_filter", products.product_filter, name="vproducts_filter"),
    path("vproducts/", products.index, name="vproducts"),
    path("mvproducts-table/", ProductsListJson.as_view(), name="mvproducts-table"),
    path("vvproducts_filter", products.vendor_filter, name="vvproducts_filter"),
    path("vvproducts/", products.vindex, name="vvproducts"),
    path("vstorproducts/", products.addrecord, name="vstorproducts"),
    path("vproductsedit/<int:id>", products.edita, name="vproductsedit"),
    path("vupdateproducts", products.updaterecord, name="vupdateproducts"),
    path("vdeleteproducts/<int:id>", products.delete, name="vdeleteproducts"),
    path("vnew_orders/", order.index, name="vnew_orders"),
    path("mhcusts/", order.getcusts, name="mhcusts"),
    path("mcustomer/", order.cartmeta, name="mcustomer"),
    path("vsearch/", order.search, name="vsearch"),
    path("additem/", order.additem, name="additem"),
    path("vnums/", order.c_quantity, name="vnums"),
    path("vdelcartitem/<int:id>", order.delete, name="vdelcartitem"),
    path("vempty/<int:id>", order.delall, name="vempty"),
    path("vemptyx/<int:id>", order.delallx, name="vemptyx"),
    path("vcreate_order_c/", order.createorder, name="vcreate_order_c"),
    path("mnreviews/", order.allreviews, name="mnreviews"),
    path("mcheckreviews/<int:id>", order.checkreview, name="mcheckreviews"),
    path("activatereview/<int:id>", order.activate, name="activatereview"),
    path("vorder_summary/<str:serial>", order.order_detail, name="vorder_summary"),
    path("vporders", deliver.index, name="vporders"),
    path("unorders", deliver.unorders, name="unorders"),
    path("assignorders", deliver.assign, name="assignorders"),
    path("vpdels", deliver.delivery, name="vpdels"),
    path("vdeliver/<str:id>", deliver.delivered, name="vdeliver"),
    path("vordersedit/<str:id>", deliver.edita, name="vordersedit"),
    path("vupdateorders", deliver.updaterecord, name="vupdateorders"),
    path("vuporders", deliver.uprecord, name="vuporders"),
    path("vodelays", deliver.delayed_dispatch, name="vodelays"),
    path("vddelays", deliver.delayed_delivery, name="vddelays"),
    path("vovdelays", deliver.delay, name="vovdelays"),
    path("vorderfilter", deliver.order_filter, name="vorderfilter"),
    path("vorders", deliver.vorders, name="vorders"),
    path("vssfilter", deliver.sales_Shop_filter, name="vssfilter"),
    path("vsalesreg", deliver.sales_report, name="vsalesreg"),
    path("vsvfilter", deliver.sales_Vendor_filter, name="vsvfilter"),
    path("vvsalesreg", deliver.vsales_report, name="vvsalesreg"),
    path("vofilter", deliver.vendor_order_filter, name="vofilter"),
    path("vvorders", deliver.vendororders, name="vvorders"),
    path("act_filter", deliver.customer_filter, name="act_filter"),
    path("xdel/<int:id>", deliver.delete, name="xdel"),
    path("xadel/<int:id>", deliver.xdelete, name="xadel"),
    path("vorder_dispatch/<str:id>", deliver.mdispatch, name="vorder_dispatch"),
    path("mvtracker", deliver.tracker, name="mvtracker"),
    path("mvconfdelivery/<int:id>", deliver.dconf, name="mvconfdelivery"),
    path("mvtrackerdelays", deliver.dtracker, name="mvtrackerdelays"),
    path("mvtrackercompleted", deliver.ctracker, name="mvtrackercompleted"),
    path("verifydel", deliver.torders, name="verifydel"),
    path("verifydelivery/<str:id>", deliver.vtracker, name="verifydelivery"),
    path("mverifydel/<str:id>", deliver.vconf, name="mverifydel"),
    path("vfcomplete", deliver.forders, name="vfcomplete"),
    path("partner_fields/", esettings.index, name="partner_fields"),
    path("storefield/", esettings.addrecord, name="storefield"),
    path("fieldedit/<int:id>", esettings.edita, name="fieldedit"),
    path("updatefield", esettings.updaterecord, name="updatefield"),
    path("deletefield/<int:id>", esettings.delete, name="deletefield"),
    path("tech_skills/", esettings.sindex, name="tech_skills"),
    path("storeskill/", esettings.saddrecord, name="storeskill"),
    path("skilledit/<int:id>", esettings.sedita, name="skilledit"),
    path("updateskill", esettings.supdaterecord, name="updateskill"),
    path("deleteskill/<int:id>", esettings.sdelete, name="deleteskill"),
    path("req_certs/", esettings.cindex, name="req_certs"),
    path("storecert/", esettings.caddrecord, name="storecert"),
    path("certedit/<int:id>", esettings.cedita, name="certedit"),
    path("updatecert", esettings.cupdaterecord, name="updatecert"),
    path("deletecert/<int:id>", esettings.cdelete, name="deletecert"),
    path("work_days/", esettings.wdindex, name="work_days"),
    path("storedays/", esettings.wdaddrecord, name="storedays"),
    path("daysedit/<int:id>", esettings.wdedita, name="daysedit"),
    path("updatedays", esettings.wdupdaterecord, name="updatedays"),
    path("deletedays/<int:id>", esettings.wddelete, name="deletedays"),
    path("ecategory/", esettings.ecindex, name="ecategory"),
    path("estorecat/", esettings.ecaddrecord, name="estorecat"),
    path("ecatedit/<int:id>", esettings.ecedita, name="ecatedit"),
    path("eupdatecat", esettings.ecupdaterecord, name="eupdatecat"),
    path("edeletecat/<int:id>", esettings.ecdelete, name="edeletecat"),
    path("mexperts/", eaccounts.index, name="mexperts"),
    path("mgetskills/<int:id>", getskills, name="mgetskills"),
    path("mgetskillsx/<str:id>", getskillsx, name="mgetskillsx"),
    path("storeexpert/", users.addexpert, name="storeexpert"),
    path("mstorecontractor/", users.addcontractor, name="mstorecontractor"),
    path("mupdatecontractor", users.updatecontractor, name="mupdatecontractor"),
    path("euseredit/<int:id>", eaccounts.edita, name="euseredit"),
    path("conuseredit/<int:id>", eaccounts.conedita, name="conuseredit"),
    path("maddcontractor_meta", eaccounts.addcontractorcompany, name="maddcontractor_meta"),
    path("mcaddcontractor_meta", eaccounts.addcontractormeta, name="mcaddcontractor_meta"),
    path("updateexperts", users.updateexperts, name="updateexperts"),
    path("edocs/<int:id>", eaccounts.edocs, name="edocs"),
    path("docsview/<int:id>", eaccounts.docsview, name="docsview"),
    path("mexpertmetaedit/<int:id>", medit, name="mexpertmetaedit"),
    path("meditexpertmeta", eaccounts.editmeta, name="meditexpertmeta"),
    path("mapprovemeta_doc", eaccounts.editameta, name="mapprovemeta_doc"),
    path("meskilledit/<int:id>", sedit, name="meskilledit"),
    path("meskillupdate", editskill, name="meskillupdate"),
    path("meskillchange", eaccounts.changeskill, name="meskillchange"),
    path("medocsadd", eaccounts.addcerts, name="medocsadd"),
    path("medeletedoc/<int:id>", delete, name="medeletedoc"),
    path("metimesadd", eaccounts.addtimes, name="metimesadd"),
    path("medeletetime/<int:id>", tdelete, name="medeletetime"),
    path("p_expert_filter", eaccounts.pending_filter, name="p_expert_filter"),
    path("expert_filter", eaccounts.expert_filter, name="expert_filter"),
    path("f_expert_filter", eaccounts.fpending_filter, name="f_expert_filter"),
    path("fexpert_filter", eaccounts.fexpert_filter, name="fexpert_filter"),
    path("mexpertsp/", eaccounts.pindex, name="mexpertsp"),
    path("exp_jobs/", ejobs.index, name="exp_jobs"),
    path("gigsreview/<int:id>", ejobs.edita, name="gigsreview"),
    path("upgigsreview/", ejobs.upreview, name="upgigsreview"),
    path("qrequests/", ejobs.open, name="qrequests"),
    path("unreviewed/", ejobs.newquotes, name="unreviewed"),
    path("create_quote/<int:id>", ejobs.create_quote, name="create_quote"),
    path("create_quote_c/", ejobs.storequote, name="create_quote_c"),
    path("mquote_summary/<uidb64>", ejobs.quote_detail, name="mquote_summary"),
    path("iquotes/<int:id>", ejobs.iquotes, name="iquotes"),
    path("nquotes/<int:id>", ejobs.nquotes, name="nquotes"),
    path("macceptquote/<int:id>", ejobs.confirm, name="macceptquote"),
    path("mselectquote/<int:id>", ejobs.approve, name="mselectquote"),
    path("xmiles_summary/<uidb64>", ejobs.miles_detail, name="xmiles_summary"),
    path("active_jobs/", ejobs.active, name="active_jobs"),
    path("excat/", ecats.index, name="excat"),
    path("excats/", EcatDataTableView.as_view(), name="excats"),
    path("storexcat/", ecats.addrecord, name="storexcat"),
    path("excatedit/<int:id>", ecats.edita, name="excatedit"),
    path("updatexcat", ecats.updaterecord, name="updatexcat"),
    path("deletexcat/<int:id>", ecats.delete, name="deletexcat"),
    path("exskill/", eskills.index, name="exskill"),
    path("exskills/", EskillsDataTableView.as_view(), name="exskills"),
    path("storexskill/", eskills.addrecord, name="storexskill"),
    path("exskilledit/<int:id>", eskills.edita, name="exskilledit"),
    path("updatexskill", eskills.updaterecord, name="updatexskill"),
    path("deletexskill/<int:id>", eskills.delete, name="deletexskill"),
    path("deletemreq/<int:id>", ejobs.delete, name="deletemreq"),
    path("legal_types/", legald.get_legal_document_types, name="legal_types"),
    path("types_table/", LegalDocumentTypesDataTableView.as_view(), name="types_table"),
    path("storelegaltype/", legald.add_legal_document_type, name="storelegaltype"),
    path("legaltypeedit/<int:id>", legald.editatype, name="legaltypeedit"),
    path("updatelegaltype", legald.update_legal_document_type, name="updatelegaltype"),
    path(
        "deletelegaltype/<int:id>",
        legald.delete_legal_document_type,
        name="deletelegaltype",
    ),
    path("legal_docs/", legald.get_legal_documents, name="legal_docs"),
    path("docs_table/", LegalDocumentsDataTableView.as_view(), name="docs_table"),
    path("storedocs/", legald.add_legal_document, name="storedocs"),
    path("docsedit/<int:id>", legald.editadocument, name="docsedit"),
    path("updatedocs", legald.update_legal_document, name="updatedocs"),
    path("deletedocs/<int:id>", legald.delete_legal_document, name="deletedocs"),
    path("sms/", sms.index, name="sms"),
    path("sms_table/", SMSListJson.as_view(), name="sms_table"),
    path("sendsms/", sms.send_sms, name="sendsms"),
    path("deletesms/<int:id>", sms.delete, name="deletesms"),
    path("mhall/", sms.getall, name="mhall"),
    path("export-vproducts/<int:id>", shops.export_vproducts, name="export-vproducts"),
    path(
        "export-vproducts-vendor/<int:id>",
        shops.export_vendor_products,
        name="export-vproducts-vendor",
    ),
    path("upload-vproducts/", shops.upload_vproducts, name="upload-vproducts"),
    path(
        "export-products-master/", items.export_products, name="export-products-master"
    ),
    path(
        "upload-products-master/", items.upload_products, name="upload-products-master"
    ),
    path("utypes/", roles.index, name="utypes"),
    path("utypes_table/", UsertypesDataTableView.as_view(), name="utypes_table"),
    path("storetype/", roles.addrecord, name="storetype"),
    path("typeedit/<int:id>", roles.edita, name="typeedit"),
    path("updatetype", roles.updaterecord, name="updatetype"),
    path("deletetype/<int:id>", roles.delete, name="deletetype"),
    path("rolesedit/<int:id>", roles.rolesedit, name="rolesedit"),
    path("rolesupdate", roles.rolesupdate, name="rolesupdate"),
    path("update_approval", eaccounts.approve, name="update_approval"),
]
