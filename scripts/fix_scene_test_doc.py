# -*- coding: utf-8 -*-
import copy
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ns = {"w": W}
ET.register_namespace("w", W)


def p_text(p):
    return "".join(t.text or "" for t in p.findall(".//w:t", ns)).strip()


def set_paragraph_text(p, text):
    texts = p.findall(".//w:t", ns)
    if texts:
        texts[0].text = text
        for t in texts[1:]:
            t.text = ""
    else:
        r = ET.SubElement(p, f"{{{W}}}r")
        t = ET.SubElement(r, f"{{{W}}}t")
        t.text = text


def set_cell_text(tc, text):
    paras = tc.findall("w:p", ns)
    if not paras:
        paras = [ET.SubElement(tc, f"{{{W}}}p")]
    set_paragraph_text(paras[0], text)
    for extra in paras[1:]:
        set_paragraph_text(extra, "")


def get_rows(tbl):
    return tbl.findall("w:tr", ns)


def set_row_cells(row, values):
    cells = row.findall("w:tc", ns)
    for i, val in enumerate(values):
        if i < len(cells):
            set_cell_text(cells[i], val)


def build_second_table(base_tbl, data):
    tbl = copy.deepcopy(base_tbl)
    rows = get_rows(tbl)

    set_row_cells(rows[0], ["用例说明", data["desc"]])
    set_row_cells(rows[1], ["前提和约束", data["pre"]])
    set_row_cells(rows[2], ["过程终止条件", data["stop"]])
    set_row_cells(rows[3], ["评价标准", data["standard"]])
    set_row_cells(rows[4], ["步骤", "用例步骤", "预期测试结果", "实际测试结果", "问题标记"])

    step_template = copy.deepcopy(rows[5])
    screenshot_row = rows[9]

    for r in rows[5:9]:
        tbl.remove(r)

    insert_at = list(tbl).index(screenshot_row)
    for i, step in enumerate(data["steps"], start=1):
        new_row = copy.deepcopy(step_template)
        set_row_cells(new_row, [f"步骤{i}", step[0], step[1], "与预期结果一致", ""])
        tbl.insert(insert_at, new_row)
        insert_at += 1

    rows = get_rows(tbl)
    set_row_cells(rows[-3], ["实测截图", ""])
    set_row_cells(rows[-2], ["是否发生重启动 ☐", "重启动是否成功 ☐", "是否发生失效 ☐", "是否发生故障 ☐", "是否发生重启动 ☐"])
    set_row_cells(rows[-1], ["测试结论", "✔通过        ☐ 基本通过        ☐ 不通过"])
    return tbl


def main():
    base = Path(r"e:\sheep\All-Sheep\__paper_edit_backup_before_662.docx")
    out = Path(r"e:\sheep\All-Sheep\__paper_fixed_662.docx")
    shutil.copyfile(base, out)

    with zipfile.ZipFile(out, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    root = ET.fromstring(files["word/document.xml"])
    body = root.find("w:body", ns)
    children = list(body)

    idx_67 = next(i for i, c in enumerate(children) if c.tag == f"{{{W}}}p" and p_text(c).startswith("6.7"))

    intro_template = copy.deepcopy(children[454])
    caption_template = copy.deepcopy(children[455])
    head_table_template = children[456]
    blank_template = copy.deepcopy(children[457])
    cont_caption_template = copy.deepcopy(children[458])
    body_table_template = children[459]

    intro_text = (
        "基于上一节所设计的场景测试用例，对盐池县生态羊源溯源与交易平台进行了逐项执行测试。"
        "测试结果表明，系统在登录认证、全流程溯源、定制领养、购物车与结算、智能问答、养殖户申请审核、"
        "养殖档案维护以及订单协同处理等典型业务场景下，均能够按照预期完成相关操作，整体业务流程完整，"
        "数据流转正确，权限控制有效。"
    )
    common_stop = "1. 顺序执行该测试用例步骤过程中客户端宕机；2. 顺序执行该测试用例步骤完毕；3. 顺序执行该测试用例步骤过程中出现 BUG"
    common_std = "实测结果与预期测试结果相符为通过，反之为不通过"

    entries = [
        {
            "cap1": "表 6.15 用户登录与访问控制场景测试用例表",
            "cap2": "续表 6.15 用户登录与访问控制场景测试用例表",
            "trace": "系统是否能够正确处理小程序端授权登录，以及 Web 端不同角色账号的登录与访问控制",
            "case_id": "Sc-Lg-01 / Sc-Lg-02",
            "desc": "测试普通用户、待审核养殖户、已审核养殖户及管理员在登录系统和访问受限页面时，系统是否能够进行正确放行或拦截",
            "pre": "1. 系统平台（包含前后端及数据库）部署完毕，并配置正确2. 系统正常启动3. 数据库中已提前预置普通用户、待审核养殖户、已审核养殖户及管理员账号",
            "stop": common_stop,
            "standard": common_std,
            "steps": [
                ("在小程序端点击“微信手机号一键登录”并允许授权", "成功进入小程序主页"),
                ("在 Web 端登录页输入管理员账号密码并登录", "成功进入管理员后台管理页面"),
                ("在 Web 端登录页输入待审核养殖户账号密码", "系统提示该账号暂无权限，停留在登录页面"),
                ("在 Web 端登录页输入已审核通过的养殖户账号密码", "成功进入养殖户管理页面"),
                ("使用普通用户尝试直接访问后台管理页面", "系统拒绝访问并提示权限不足"),
            ],
        },
        {
            "cap1": "表 6.16 全流程溯源场景测试用例表",
            "cap2": "续表 6.16 全流程溯源场景测试用例表",
            "trace": "系统是否能够正确完成羊只溯源查询，并展示完整档案信息",
            "case_id": "Sc-Tr-01 / Sc-Tr-02",
            "desc": "测试消费者通过输入耳标编号或扫码进入溯源页面时，系统是否能够正确返回羊只基础信息及养殖过程数据",
            "pre": "1. 系统平台（包含前后端及数据库）部署完毕，并配置正确2. 系统正常启动3. 数据库中已存在带耳标编号的羊只档案，以及对应的成长、饲喂和疫苗记录",
            "stop": common_stop,
            "standard": common_std,
            "steps": [
                ("用户输入正确的耳标编号进行查询", "成功返回对应羊只的溯源信息"),
                ("用户扫码进入羊只溯源详情页面", "成功展示羊只基础档案信息"),
                ("查看成长记录、饲喂记录及疫苗接种记录", "相关养殖过程数据完整显示"),
                ("输入不存在的耳标编号进行查询", "系统提示未查询到对应羊只信息"),
            ],
        },
        {
            "cap1": "表 6.17 定制领养筛选与羊只浏览场景测试用例表",
            "cap2": "续表 6.17 定制领养筛选与羊只浏览场景测试用例表",
            "trace": "系统是否能够正确完成羊只筛选、目标定位与详情浏览",
            "case_id": "Sc-Ad-01 / Sc-Ad-02",
            "desc": "测试普通用户在定制领养模块中按照筛选条件查找羊只，并查看羊只详情时系统的响应是否正常",
            "pre": "1. 系统平台（包含前后端及数据库）部署完毕，并配置正确2. 系统正常启动3. 数据库中已存在多只不同体征条件的羊只数据",
            "stop": common_stop,
            "standard": common_std,
            "steps": [
                ("进入定制领养页面并设置筛选条件", "成功返回符合条件的羊只列表"),
                ("点击目标羊只进入详情页", "成功进入羊只详情页面"),
                ("查看羊只体重、身高、体长、价格等信息", "相关信息显示完整且正确"),
                ("设置无匹配条件进行筛选", "系统显示无匹配结果或空列表"),
            ],
        },
        {
            "cap1": "表 6.18 羊只加入购物车与领养状态场景测试用例表",
            "cap2": "续表 6.18 羊只加入购物车与领养状态场景测试用例表",
            "trace": "系统是否能够正确判断羊只当前领养状态，并完成加入购物车等操作",
            "case_id": "Sc-Ca-01 / Sc-Ca-02",
            "desc": "测试普通用户查看羊只领养状态、将羊只加入购物车以及查看购物车内容时，系统处理是否正常",
            "pre": "1. 系统平台（包含前后端及数据库）部署完毕，并配置正确2. 系统正常启动3. 数据库中已存在可领养羊只，测试账号已完成登录",
            "stop": common_stop,
            "standard": common_std,
            "steps": [
                ("进入羊只详情页查看当前领养状态", "系统正确显示该羊只的当前领养状态"),
                ("点击“加入购物车”按钮", "羊只成功加入购物车"),
                ("进入购物车页面查看已添加羊只", "购物车正确显示对应羊只信息"),
                ("对已被他人领养的羊只再次尝试加入购物车", "系统阻止重复领养并给出提示"),
            ],
        },
        {
            "cap1": "表 6.19 优惠券与余额支付场景测试用例表",
            "cap2": "续表 6.19 优惠券与余额支付场景测试用例表",
            "trace": "系统是否能够正确完成优惠券校验、余额支付和订单生成",
            "case_id": "Sc-Pa-01 / Sc-Pa-02",
            "desc": "测试普通用户在结算过程中填写收货信息、使用优惠券并通过余额支付完成下单时，系统逻辑是否正确",
            "pre": "1. 系统平台（包含前后端及数据库）部署完毕，并配置正确2. 系统正常启动3. 测试账号已登录，购物车中已有待结算商品，且账户中存在可用余额及优惠券",
            "stop": common_stop,
            "standard": common_std,
            "steps": [
                ("进入结算页面并填写收货人、联系方式和收货地址", "系统允许继续进入支付流程"),
                ("选择满足使用条件的优惠券", "订单金额按照规则正确减免"),
                ("选择余额支付并提交订单", "订单创建成功，支付完成"),
                ("选择不满足使用条件的优惠券", "系统提示优惠券不可用"),
                ("在账户余额不足时提交订单", "系统提示余额不足，无法完成支付"),
            ],
        },
        {
            "cap1": "表 6.20 智能问答使用场景测试用例表",
            "cap2": "续表 6.20 智能问答使用场景测试用例表",
            "trace": "系统是否能够正确响应用户的业务咨询和农业知识问答",
            "case_id": "Sc-QA-01 / Sc-QA-02",
            "desc": "测试用户在智能问答模块中进行平台业务咨询及滩羊养殖知识提问时，系统回答是否准确且响应正常",
            "pre": "1. 系统平台（包含前后端及数据库）部署完毕，并配置正确2. 系统正常启动3. 智能问答模块及相关知识库已完成部署并可正常调用",
            "stop": common_stop,
            "standard": common_std,
            "steps": [
                ("输入平台业务相关问题，如“我的订单在哪里查看”", "系统返回与业务流程相符的回答"),
                ("输入农业知识相关问题，如“滩羊适合什么饲料”", "系统返回与知识库内容相符的回答"),
                ("连续进行多轮提问", "系统能够持续响应，整体交互过程正常"),
            ],
        },
        {
            "cap1": "表 6.21 养殖户申请入驻与审核场景测试用例表",
            "cap2": "续表 6.21 养殖户申请入驻与审核场景测试用例表",
            "trace": "系统是否能够正确完成养殖户申请、审核及角色状态流转",
            "case_id": "Sc-Br-01 / Sc-Br-02",
            "desc": "测试普通用户申请成为养殖户，以及管理员对申请信息进行审核时，系统处理是否正常",
            "pre": "1. 系统平台（包含前后端及数据库）部署完毕，并配置正确2. 系统正常启动3. 数据库中已存在普通用户账号和管理员账号",
            "stop": common_stop,
            "standard": common_std,
            "steps": [
                ("普通用户在小程序端提交养殖户申请", "账号状态变为待审核"),
                ("管理员进入审核页面查看申请资料", "能够正常查看对应申请信息"),
                ("管理员执行“通过”操作", "目标账号成为已审核养殖户"),
                ("管理员执行“驳回”操作", "目标账号被回退为普通用户或保持不可使用养殖功能状态"),
            ],
        },
        {
            "cap1": "表 6.22 养殖档案维护场景测试用例表",
            "cap2": "续表 6.22 养殖档案维护场景测试用例表",
            "trace": "系统是否能够正确完成羊只档案及养殖记录维护，并实现数据归属隔离",
            "case_id": "Sc-Ar-01 / Sc-Ar-02",
            "desc": "测试审核通过后的养殖户对本人名下羊只档案、成长记录、饲喂记录和疫苗记录进行维护时，系统处理是否正常",
            "pre": "1. 系统平台（包含前后端及数据库）部署完毕，并配置正确2. 系统正常启动3. 养殖户账号已审核通过，并能够正常登录养殖管理页面",
            "stop": common_stop,
            "standard": common_std,
            "steps": [
                ("新增本人名下羊只基础档案", "羊只档案保存成功"),
                ("新增成长记录", "成长记录保存成功并可正常查看"),
                ("新增饲喂记录", "饲喂记录保存成功并可正常查看"),
                ("新增疫苗接种记录", "疫苗记录保存成功并可正常查看"),
                ("尝试访问其他养殖户名下羊只或相关记录", "系统拒绝访问并提示无权限"),
            ],
        },
        {
            "cap1": "表 6.23 订单协同处理与权限控制场景测试用例表",
            "cap2": "续表 6.23 订单协同处理与权限控制场景测试用例表",
            "trace": "系统是否能够正确支持养殖户订单协同处理，并限制越权操作",
            "case_id": "Sc-Or-01 / Sc-Or-02",
            "desc": "测试养殖户查看本人相关订单、填写物流信息、更新订单状态以及系统对越权操作的拦截是否正常",
            "pre": "1. 系统平台（包含前后端及数据库）部署完毕，并配置正确2. 系统正常启动3. 数据库中已存在与养殖户名下羊只相关的订单数据，且养殖户账号已审核通过",
            "stop": common_stop,
            "standard": common_std,
            "steps": [
                ("养殖户进入订单管理页面查看本人相关订单", "成功显示与本人羊只相关的订单信息"),
                ("填写物流公司和运单号，并将订单状态更新为发货中", "订单状态更新成功，物流信息保存正确"),
                ("继续将订单状态更新为已完成", "订单状态正确变更"),
                ("尝试处理不属于本人羊只的订单", "系统拒绝操作并提示无权限"),
            ],
        },
    ]

    new_nodes = [copy.deepcopy(blank_template)]
    intro = copy.deepcopy(intro_template)
    set_paragraph_text(intro, intro_text)
    new_nodes.extend([intro, copy.deepcopy(blank_template)])

    for entry in entries:
        cap1 = copy.deepcopy(caption_template)
        set_paragraph_text(cap1, entry["cap1"])

        tbl1 = copy.deepcopy(head_table_template)
        set_row_cells(get_rows(tbl1)[0], ["测试需求追踪", entry["trace"], "用例编号", entry["case_id"]])

        cap2 = copy.deepcopy(cont_caption_template)
        set_paragraph_text(cap2, entry["cap2"])

        tbl2 = build_second_table(body_table_template, entry)
        new_nodes.extend([cap1, tbl1, copy.deepcopy(blank_template), cap2, tbl2, copy.deepcopy(blank_template)])

    for offset, node in enumerate(new_nodes):
        body.insert(idx_67 + offset, node)

    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)

    print(out)


if __name__ == "__main__":
    main()
