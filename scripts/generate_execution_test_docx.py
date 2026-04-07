from pathlib import Path
from xml.sax.saxutils import escape
import zipfile


NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def text_run(text: str, bold: bool = False) -> str:
    text = escape(text)
    rpr = (
        "<w:rPr><w:b/></w:rPr>" if bold else ""
    )
    return f'<w:r>{rpr}<w:t xml:space="preserve">{text}</w:t></w:r>'


def paragraph(text: str = "", center: bool = False, bold: bool = False) -> str:
    jc = '<w:jc w:val="center"/>' if center else ""
    return f"<w:p><w:pPr>{jc}</w:pPr>{text_run(text, bold=bold)}</w:p>"


def table_cell(text: str, width: int, shaded: bool = False, center: bool = False) -> str:
    shd = '<w:shd w:val="clear" w:color="auto" w:fill="F0F0F0"/>' if shaded else ""
    jc = '<w:jc w:val="center"/>' if center else ""
    return (
        "<w:tc>"
        f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shd}<w:vAlign w:val="center"/></w:tcPr>'
        f"<w:p><w:pPr>{jc}</w:pPr>{text_run(text)}</w:p>"
        "</w:tc>"
    )


def table_cell_span(
    text: str, width: int, span: int, shaded: bool = False, center: bool = False
) -> str:
    shd = '<w:shd w:val="clear" w:color="auto" w:fill="F0F0F0"/>' if shaded else ""
    jc = '<w:jc w:val="center"/>' if center else ""
    return (
        "<w:tc>"
        f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/><w:gridSpan w:val="{span}"/>{shd}<w:vAlign w:val="center"/></w:tcPr>'
        f"<w:p><w:pPr>{jc}</w:pPr>{text_run(text)}</w:p>"
        "</w:tc>"
    )


def table_row(cells: list[str]) -> str:
    return "<w:tr>" + "".join(cells) + "</w:tr>"


def make_table(rows: list[str], widths: list[int]) -> str:
    tbl_pr = (
        "<w:tblPr>"
        '<w:tblW w:w="0" w:type="auto"/>'
        "<w:tblBorders>"
        '<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:left w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:right w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:insideV w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        "</w:tblBorders>"
        "</w:tblPr>"
    )
    grid = "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"
    return "<w:tbl>" + tbl_pr + grid + "".join(rows) + "</w:tbl>"


def build_meta_table(
    trace: str,
    case_id: str,
    description: str,
    preconditions: list[str],
) -> str:
    widths = [1400, 6200, 1600, 3400]
    rows = [
        table_row(
            [
                table_cell("测试需求追踪", widths[0], shaded=True, center=True),
                table_cell(trace, widths[1], center=False),
                table_cell("用例编号", widths[2], shaded=True, center=True),
                table_cell(case_id, widths[3], center=True),
            ]
        ),
        table_row(
            [
                table_cell("用例说明", widths[0], shaded=True, center=True),
                table_cell_span(description, widths[1] + widths[2] + widths[3], 3),
            ]
        ),
        table_row(
            [
                table_cell("前提和约束", widths[0], shaded=True, center=True),
                table_cell_span("\n".join(preconditions), widths[1] + widths[2] + widths[3], 3),
            ]
        ),
        table_row(
            [
                table_cell("过程终止条件", widths[0], shaded=True, center=True),
                table_cell_span(
                    "1. 顺序执行该测试用例步骤过程中客户端或服务端宕机；\n"
                    "2. 顺序执行该测试用例步骤完毕；\n"
                    "3. 顺序执行该测试用例步骤过程中出现BUG；",
                    widths[1] + widths[2] + widths[3],
                    3,
                ),
            ]
        ),
        table_row(
            [
                table_cell("评价标准", widths[0], shaded=True, center=True),
                table_cell_span(
                    "实测结果与预期测试结果相符为通过，反之为不通过",
                    widths[1] + widths[2] + widths[3],
                    3,
                ),
            ]
        ),
    ]
    return make_table(rows, widths)


def build_steps_table(steps: list[tuple[str, str, str, str, str]]) -> str:
    widths = [900, 3800, 3200, 2200, 1200]
    rows = [
        table_row(
            [
                table_cell("步骤", widths[0], shaded=True, center=True),
                table_cell("用例步骤", widths[1], shaded=True, center=True),
                table_cell("预期测试结果", widths[2], shaded=True, center=True),
                table_cell("实际测试结果", widths[3], shaded=True, center=True),
                table_cell("问题标记", widths[4], shaded=True, center=True),
            ]
        )
    ]
    for step_no, action, expected, actual, mark in steps:
        rows.append(
            table_row(
                [
                    table_cell(step_no, widths[0], center=True),
                    table_cell(action, widths[1]),
                    table_cell(expected, widths[2]),
                    table_cell(actual, widths[3], center=True),
                    table_cell(mark, widths[4], center=True),
                ]
            )
        )
    return make_table(rows, widths)


def build_tail_table() -> str:
    widths = [1400, 1125, 1125, 1125, 1125, 1125]
    rows = [
        table_row(
            [
                table_cell("实测截图", widths[0], shaded=True, center=True),
                table_cell_span("此处插入对应角色执行测试截图。", sum(widths[1:]), 5),
            ]
        ),
        table_row(
            [
                table_cell("是否发生重启动 ☐", widths[0], center=True),
                table_cell("重启动是否成功 ☐", widths[1], center=True),
                table_cell("是否发生失效 ☐", widths[2], center=True),
                table_cell("是否发生故障 ☐", widths[3], center=True),
                table_cell_span("是否发生重启动 ☐", widths[4] + widths[5], 2, center=True),
            ]
        ),
        table_row(
            [
                table_cell("测试结论", widths[0], shaded=True, center=True),
                table_cell_span("✔ 通过        ☐ 基本通过        ☐ 不通过", sum(widths[1:]), 5, center=True),
            ]
        ),
    ]
    return make_table(rows, widths)


def section(
    title: str,
    trace: str,
    case_id: str,
    description: str,
    preconditions: list[str],
    steps: list[tuple[str, str, str, str, str]],
) -> str:
    return (
        paragraph(title, center=True, bold=True)
        + build_meta_table(trace, case_id, description, preconditions)
        + paragraph("")
        + build_steps_table(steps)
        + paragraph("")
        + build_tail_table()
        + paragraph("")
        + paragraph("")
    )


def build_document_xml() -> str:
    body = []
    body.append(paragraph("6.3.2 执行测试", bold=True))
    body.append(paragraph("基于上一节所设计的三个角色场景测试用例表进行执行测试。"))

    body.append(
        section(
            "表 6.12 普通用户核心业务执行测试表",
            "系统是否能够正确支持普通用户在微信小程序端完成智能问答、定制领养、订单支付、订单查询及溯源查询等核心业务操作",
            "Sc-wx-user-01",
            "测试普通用户在微信小程序端“智能问答”和“定制领养”两条核心业务链路是否能够正确执行，并验证登录、支付、订单及溯源等关键异常处理是否正常。",
            [
                "1. 系统平台（包含小程序前端、后端服务及数据库）部署完毕，并配置正确。",
                "2. 微信小程序可正常启动并访问后端接口。",
                "3. 数据库中已存在普通用户测试账号、可领养羊只、优惠券及订单测试数据。",
                "4. 测试账号具备可覆盖“余额充足”和“余额不足”两种测试场景的数据条件。",
            ],
            [
                ("步骤1", "进入微信小程序首页，点击“智能问答”，输入问题并发送", "系统成功返回问答结果，页面正常显示回答内容", "与预期结果一致", "无"),
                ("步骤2", "从首页进入“定制领养”，浏览羊只并在未登录状态下尝试领养或下单", "系统提示用户先登录，并跳转到登录页", "与预期结果一致", "无"),
                ("步骤3", "在登录页点击“微信手机号一键登录”，允许授权后继续操作", "登录成功，返回业务页面，用户可继续领养流程", "与预期结果一致", "无"),
                ("步骤4", "选择目标羊只加入购物车，进入订单确认页填写完整收货信息并提交订单", "系统成功生成订单，并完成支付处理", "与预期结果一致", "无"),
                ("步骤5", "在订单确认页选择不可用优惠券或构造余额不足场景后提交订单", "系统提示优惠券不可用或余额不足，不会错误完成支付", "与预期结果一致", "无"),
                ("步骤6", "进入“我的订单”“我的羊”页面，并对已领养羊只执行溯源查询", "系统正确显示订单、我的羊及溯源信息", "与预期结果一致", "无"),
            ],
        )
    )

    body.append(
        section(
            "表 6.13 养殖户核心业务执行测试表",
            "系统是否能够正确支持养殖户完成后台登录、本人羊只档案管理、养殖记录维护及相关订单处理等核心业务操作",
            "Sc-web-breeder-01",
            "测试养殖户在后台管理端“登录后台、管理本人羊只、录入养殖记录、处理本人相关订单”的核心业务链路是否能够正确执行，并验证待审核账号与越权访问等异常情况是否被正确拦截。",
            [
                "1. 系统平台（包含前后端及数据库）部署完毕，并配置正确。",
                "2. 后台管理系统可正常访问。",
                "3. 数据库中已预置已审核通过养殖户账号、未审核通过养殖户账号、本人羊只测试数据及订单测试数据。",
                "4. 测试环境中存在至少一条与养殖户本人羊只相关的订单记录。",
            ],
            [
                ("步骤1", "在后台登录页输入已审核通过的养殖户账号和正确密码后登录", "系统登录成功，进入养殖户工作台", "与预期结果一致", "无"),
                ("步骤2", "使用未审核通过的养殖户账号登录后台", "系统拒绝登录，并提示该养殖户账号正在审核中", "与预期结果一致", "无"),
                ("步骤3", "进入羊只管理模块，对本人名下羊只执行新增或修改操作", "系统成功保存本人羊只档案信息", "与预期结果一致", "无"),
                ("步骤4", "在羊只详情页录入生长记录、喂养记录和免疫记录", "系统成功保存相关养殖记录，并在对应页面正确显示", "与预期结果一致", "无"),
                ("步骤5", "进入订单管理模块，查看与本人羊只相关订单并更新订单状态，发货时填写物流信息", "系统成功更新订单状态，并正确保存物流公司与物流单号", "与预期结果一致", "无"),
                ("步骤6", "尝试访问或修改非本人羊只数据、非本人相关订单", "系统拒绝访问或修改，并提示无权限操作", "与预期结果一致", "无"),
            ],
        )
    )

    body.append(
        section(
            "表 6.14 管理员核心业务执行测试表",
            "系统是否能够正确支持管理员完成后台登录、养殖户审核、用户角色管理及平台全局资源查看等核心业务操作",
            "Sc-web-admin-01",
            "测试管理员在后台管理端“登录后台、审核养殖户申请、管理用户角色、查看全局订单与平台资源”的核心业务链路是否能够正确执行，并验证非管理员访问及高风险角色修改操作是否被正确限制。",
            [
                "1. 系统平台（包含前后端及数据库）部署完毕，并配置正确。",
                "2. 后台管理系统可正常访问。",
                "3. 数据库中已存在管理员测试账号、普通用户账号、养殖户账号及待审核养殖户申请数据。",
                "4. 数据库中已存在用户、羊只及订单等全局资源测试数据。",
            ],
            [
                ("步骤1", "在后台登录页输入正确的管理员账号和密码后登录", "系统登录成功，进入管理员后台首页", "与预期结果一致", "无"),
                ("步骤2", "使用普通用户或养殖户账号尝试登录后台管理端", "系统拒绝访问后台，并提示无权限访问", "与预期结果一致", "无"),
                ("步骤3", "进入养殖户申请审核模块，查看待审核列表并打开某申请详情页", "系统正确显示待审核养殖户列表及详细资料", "与预期结果一致", "无"),
                ("步骤4", "对待审核养殖户申请分别执行“通过”与“拒绝”操作", "系统正确保存审核结果，并更新对应用户状态", "与预期结果一致", "无"),
                ("步骤5", "进入角色管理模块，修改目标用户角色", "系统成功更新目标用户角色信息", "与预期结果一致", "无"),
                ("步骤6", "在角色管理模块中尝试修改管理员自己的角色", "系统拒绝该操作，并提示不能修改自己的角色", "与预期结果一致", "无"),
                ("步骤7", "进入订单管理或资源管理模块，查看平台全局订单、羊只及用户信息", "系统正确显示平台全局资源，而非仅显示个人数据", "与预期结果一致", "无"),
            ],
        )
    )

    sect_pr = (
        '<w:sectPr>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1800" w:bottom="1440" w:left="1800" w:header="851" w:footer="992" w:gutter="0"/>'
        '<w:cols w:space="425" w:num="1"/>'
        '<w:docGrid w:type="lines" w:linePitch="312" w:charSpace="0"/>'
        '</w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{NS_W}" xmlns:r="{NS_R}"><w:body>'
        + "".join(body)
        + sect_pr
        + "</w:body></w:document>"
    )


def build_docx(out_path: Path) -> None:
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
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", build_document_xml())


def main() -> None:
    out = Path(r"E:\sheep\All-Sheep\三个角色执行测试表.docx")
    build_docx(out)
    print(out)


if __name__ == "__main__":
    main()
