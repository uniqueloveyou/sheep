from pathlib import Path
from xml.sax.saxutils import escape
import zipfile


NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def p(text):
    text = escape(text)
    return (
        f'<w:p><w:r><w:t xml:space="preserve">{text}</w:t></w:r></w:p>'
    )


def tc(text, width):
    return (
        f'<w:tc>'
        f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/></w:tcPr>'
        f'{p(text)}'
        f'</w:tc>'
    )


def tr(values, widths):
    cells = "".join(tc(v, w) for v, w in zip(values, widths))
    return f"<w:tr>{cells}</w:tr>"


def table(rows, widths):
    tbl_pr = (
        "<w:tblPr>"
        "<w:tblW w:w=\"0\" w:type=\"auto\"/>"
        "<w:tblBorders>"
        "<w:top w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:left w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:right w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"000000\"/>"
        "</w:tblBorders>"
        "</w:tblPr>"
    )
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    body = "".join(tr(row, widths) for row in rows)
    return f"<w:tbl>{tbl_pr}<w:tblGrid>{grid}</w:tblGrid>{body}</w:tbl>"


def section(title, meta_rows, case_rows):
    meta_widths = [1800, 4200, 1800, 5200]
    case_widths = [900, 1500, 3600, 3600, 1800, 1600]
    out = []
    out.append(
        "<w:p><w:pPr><w:jc w:val=\"center\"/></w:pPr>"
        f"<w:r><w:rPr><w:b/></w:rPr><w:t>{escape(title)}</w:t></w:r></w:p>"
    )
    out.append(table(meta_rows, meta_widths))
    out.append(p(""))
    out.append(
        table(
            [["用例编号", "测试项", "输入动作", "预期输出", "测试结果", "备注"], *case_rows],
            case_widths,
        )
    )
    out.append(p(""))
    out.append(p(""))
    return "".join(out)


def build_document():
    sections = []

    sections.append(
        section(
            "表6.4 普通用户完整业务流程场景测试用例",
            [
                ["项目名称", "盐池县生态羊源溯源与交易平台", "用例标识", "Sc-user-01"],
                ["模块名称", "普通用户完整业务流程", "测试人员", "马晓玲"],
                ["测试类型", "场景测试", "测试方法", "黑盒测试"],
                ["测试日期", "2026-03-25", "用例目的", "验证普通用户在小程序端完成核心业务流程的正确性"],
                ["用例描述", "普通用户从进入小程序开始，依次完成登录、浏览羊只、提交领养订单、支付结算、查看个人订单与溯源信息，并验证其无法访问后台管理功能", "前置条件", "1. 小程序端运行正常；2. 系统中存在可展示羊只数据；3. 用户可正常登录；4. 用户账户中有可用余额或可领取优惠券"],
            ],
            [
                ["1", "微信登录", "点击“微信手机号一键登录”，授权登录", "登录成功，进入小程序首页", "与预期输出一致", "对应小程序登录逻辑"],
                ["2", "浏览羊只列表", "进入首页或分类页查看羊只列表", "系统正常返回羊只列表数据", "与预期输出一致", "核心功能"],
                ["3", "查看羊只详情", "点击某只羊进入详情页", "系统正常显示羊只详情、养殖户等信息", "与预期输出一致", "核心功能"],
                ["4", "提交领养订单", "进入定制领养/结算页面，填写收货信息并提交", "订单提交成功，进入支付流程", "与预期输出一致", "核心功能"],
                ["5", "余额支付或优惠券结算", "选择余额支付或使用优惠券后确认", "支付成功，订单生成，状态更新", "与预期输出一致", "核心功能"],
                ["6", "查看个人订单", "进入“我的订单”或历史订单页面查看订单", "系统仅显示当前用户自己的订单信息", "与预期输出一致", "核心功能"],
                ["7", "查看溯源信息", "进入溯源详情页查看耳标、成长、饲喂、免疫等信息", "系统正常显示对应羊只溯源信息", "与预期输出一致", "核心功能"],
                ["8", "越权访问校验", "普通用户尝试访问后台页面或非本人订单数据", "系统拒绝访问或提示无权限", "与预期输出一致", "权限控制"],
            ],
        )
    )

    sections.append(
        section(
            "表6.5 养殖户完整业务流程场景测试用例",
            [
                ["项目名称", "盐池县生态羊源溯源与交易平台", "用例标识", "Sc-breeder-01"],
                ["模块名称", "养殖户完整业务流程", "测试人员", "马晓玲"],
                ["测试类型", "场景测试", "测试方法", "黑盒测试"],
                ["测试日期", "2026-03-25", "用例目的", "验证养殖户在后台完成羊只档案维护、养殖记录维护和订单处理流程的正确性"],
                ["用例描述", "养殖户在审核通过后登录后台，依次完成本人羊只档案维护、成长记录录入、饲喂记录录入、免疫记录录入、相关订单查看与状态更新，并验证其不能操作他人数据", "前置条件", "1. 后台系统运行正常；2. 养殖户账号已审核通过；3. 后台可正常登录；4. 系统中允许维护羊只及相关记录；5. 存在与该养殖户相关的订单数据"],
            ],
            [
                ["1", "后台登录", "输入已审核通过的养殖户账号密码登录后台", "登录成功，进入养殖户首页", "与预期输出一致", "未审核账号应被拦截"],
                ["2", "查看本人羊只", "进入羊只管理列表页面", "系统仅显示当前养殖户本人名下羊只", "与预期输出一致", "核心功能"],
                ["3", "新增羊只档案", "在羊只管理页面新增羊只基础信息并保存", "羊只创建成功，生成羊只档案", "与预期输出一致", "核心功能"],
                ["4", "编辑羊只档案", "对本人羊只进行编辑并保存", "羊只信息更新成功", "与预期输出一致", "核心功能"],
                ["5", "录入成长记录", "进入羊只详情页新增成长记录", "成长记录保存成功并可查看", "与预期输出一致", "核心功能"],
                ["6", "录入饲喂记录", "进入羊只详情页新增饲喂记录", "饲喂记录保存成功并可查看", "与预期输出一致", "核心功能"],
                ["7", "录入免疫记录", "进入羊只详情页新增疫苗接种记录", "免疫记录保存成功并可查看", "与预期输出一致", "核心功能"],
                ["8", "查看相关订单", "进入订单管理页面查看订单", "系统仅显示与本人羊只相关订单", "与预期输出一致", "核心功能"],
                ["9", "更新订单状态", "填写物流公司、运单号并更新状态", "订单状态与物流信息更新成功", "与预期输出一致", "核心功能"],
                ["10", "越权访问校验", "尝试查看或修改其他养殖户羊只、记录、订单", "系统拒绝访问并提示无权限", "与预期输出一致", "权限控制"],
            ],
        )
    )

    sections.append(
        section(
            "表6.6 系统管理员完整业务流程场景测试用例",
            [
                ["项目名称", "盐池县生态羊源溯源与交易平台", "用例标识", "Sc-admin-01"],
                ["模块名称", "系统管理员完整业务流程", "测试人员", "马晓玲"],
                ["测试类型", "场景测试", "测试方法", "黑盒测试"],
                ["测试日期", "2026-03-25", "用例目的", "验证管理员在后台完成养殖户审核、用户角色管理和全局订单资源管理流程的正确性"],
                ["用例描述", "管理员登录后台后，依次完成待审核养殖户查看、审核通过或驳回、用户角色管理、全局订单查看，并验证系统对高风险管理操作的限制", "前置条件", "1. 后台系统运行正常；2. 管理员账号可正常登录；3. 系统中存在待审核养殖户数据、普通用户数据和订单数据"],
            ],
            [
                ["1", "后台登录", "输入管理员账号密码登录后台", "登录成功，进入管理员首页", "与预期输出一致", ""],
                ["2", "查看待审核养殖户", "进入养殖户审核列表页面", "系统正常显示待审核及已审核养殖户信息", "与预期输出一致", "核心功能"],
                ["3", "审核养殖户通过", "进入审核详情页，点击“通过”", "目标用户保持养殖户角色并变为已审核状态", "与预期输出一致", "核心功能"],
                ["4", "审核养殖户驳回", "进入审核详情页，点击“驳回”", "目标用户被回退为普通用户，失去养殖户后台权限", "与预期输出一致", "核心功能"],
                ["5", "查看用户角色列表", "进入角色管理页面", "系统正常显示全部用户及角色信息", "与预期输出一致", "核心功能"],
                ["6", "修改目标用户角色", "选择目标用户并修改角色后保存", "角色修改成功并生效", "与预期输出一致", "核心功能"],
                ["7", "查看全局订单", "进入订单管理页面查看订单", "系统可显示平台全部订单信息", "与预期输出一致", "核心功能"],
                ["8", "查看全局资源", "查看用户、羊只等平台资源信息", "系统正常显示全局数据", "与预期输出一致", ""],
                ["9", "高风险操作限制", "管理员尝试修改自身角色", "系统拒绝操作并提示不能修改自身角色", "与预期输出一致", "权限控制"],
            ],
        )
    )

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{NS_W}" xmlns:r="{NS_R}">'
        "<w:body>"
        + "".join(sections)
        + (
            '<w:sectPr>'
            '<w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
            'w:header="720" w:footer="720" w:gutter="0"/>'
            "</w:sectPr>"
        )
        + "</w:body></w:document>"
    )

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

    out = Path("e:/sheep/All-Sheep/三种角色场景测试表.docx")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)
    print(out)


if __name__ == "__main__":
    build_document()
