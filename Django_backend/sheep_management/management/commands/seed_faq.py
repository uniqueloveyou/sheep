from django.core.management.base import BaseCommand

from sheep_management.models import (
    QAAlias,
    QAAnswerDetail,
    QACategory,
    QAPair,
    QARelated,
)


FAQ_DATA = [
    {
        'category': ('出栏周期类', 'shipping_cycle', '围绕滩羊出栏时间与差异的常见问题'),
        'question': '滩羊一般多少个月可以出栏',
        'answer': '滩羊通常在6到8个月可以出栏。6个月左右更适合关注性价比和周转效率，8个月左右肉质更成熟、风味更足。',
        'keywords': '滩羊,出栏,几个月,多久,什么时候',
        'month_stage': '6-8个月',
        'is_hot': True,
        'aliases': ['滩羊多久可以出栏', '滩羊几个月能出栏', '滩羊什么时候可以出栏'],
        'details': [
            {
                'stage_name': '6个月',
                'weight_range': '育肥中后期参考范围',
                'nutrition_value': '肉质较嫩，脂肪适中',
                'cost_value': '整体成本较低',
                'price_value': '适合性价比型认养',
                'description': '适合更关注成本控制和出栏效率的用户',
            },
            {
                'stage_name': '8个月',
                'weight_range': '育肥完成期参考范围',
                'nutrition_value': '风味更浓，成熟度更高',
                'cost_value': '成本相对更高',
                'price_value': '适合品质型认养',
                'description': '适合更关注口感表现和肉质成熟度的用户',
            },
        ],
    },
    {
        'category': ('出栏周期类', 'shipping_cycle', '围绕滩羊出栏时间与差异的常见问题'),
        'question': '滩羊6个月可以出栏吗',
        'answer': '可以。6个月的滩羊通常已经具备基本出栏条件，养殖成本相对较低，适合追求周转效率和性价比的认养方式。',
        'keywords': '滩羊,6个月,出栏,能不能',
        'month_stage': '6个月',
        'aliases': ['六个月的滩羊能出栏吗', '滩羊养6个月能不能出栏'],
    },
    {
        'category': ('营养价值类', 'nutrition', '围绕滩羊不同月龄营养与食用品质的问题'),
        'question': '不同月龄滩羊营养价值有什么区别',
        'answer': '月龄较小的滩羊肉质更嫩、脂肪更低，月龄较大的滩羊风味更浓、营养表现更完整，适合不同的消费需求。',
        'keywords': '滩羊,月龄,营养价值,区别',
        'is_hot': True,
        'aliases': ['滩羊不同月龄的营养区别是什么', '不同月龄的滩羊有什么营养差异'],
        'details': [
            {
                'stage_name': '6个月左右',
                'nutrition_value': '肉质细嫩，蛋白质表现较好',
                'price_value': '大众接受度高',
                'description': '更适合喜欢口感细嫩、接受度高的人群',
            },
            {
                'stage_name': '8个月左右',
                'nutrition_value': '风味更足，口感层次更明显',
                'price_value': '品质感更强',
                'description': '更适合看重风味和成熟度的人群',
            },
        ],
    },
    {
        'category': ('营养价值类', 'nutrition', '围绕滩羊不同月龄营养与食用品质的问题'),
        'question': '6个月滩羊的营养特点是什么',
        'answer': '6个月滩羊通常具备蛋白质含量较好、脂肪适中、肉质偏嫩等特点，适合多数家庭日常食用。',
        'keywords': '滩羊,6个月,营养,特点',
        'month_stage': '6个月',
        'aliases': ['六个月滩羊营养怎么样', '6个月滩羊肉有什么特点'],
    },
    {
        'category': ('成本价格类', 'cost', '围绕养殖投入、阶段成本与价格形成的常见问题'),
        'question': '滩羊养到6个月成本大概是多少',
        'answer': '滩羊养到6个月的成本通常由饲料、疫苗防疫、人工和日常管理构成，整体成本一般低于8个月阶段，是比较常见的认养区间。',
        'keywords': '滩羊,6个月,成本,养殖',
        'month_stage': '6个月',
        'is_hot': True,
        'aliases': ['滩羊养6个月需要多少成本', '养到六个月成本大概多少'],
        'details': [
            {
                'stage_name': '成本构成',
                'cost_value': '饲料、防疫、人工、日常管理',
                'description': '不同养殖条件会影响实际成本，但结构基本一致',
            }
        ],
    },
    {
        'category': ('成本价格类', 'cost', '围绕养殖投入、阶段成本与价格形成的常见问题'),
        'question': '哪个阶段养殖成本增长最快',
        'answer': '通常在快速育肥阶段，饲料投入会明显增加，因此这个阶段的成本增长通常更快。',
        'keywords': '成本,增长,阶段,育肥',
        'aliases': ['滩羊哪个阶段成本涨得最快', '什么时候养殖成本增加最快'],
    },
    {
        'category': ('成本价格类', 'cost', '围绕养殖投入、阶段成本与价格形成的常见问题'),
        'question': '认养价格怎么计算',
        'answer': '认养价格通常会综合月龄、体重、饲养成本、市场参考价以及附加服务一起计算，不是只看单一因素。',
        'keywords': '认养,价格,计算,怎么算',
        'is_hot': True,
        'aliases': ['滩羊认养价格怎么算', '认养价格是怎么来的'],
        'details': [
            {
                'stage_name': '价格因素',
                'weight_range': '体重与月龄共同影响',
                'cost_value': '饲养周期越长，投入通常越高',
                'price_value': '会结合市场行情综合判断',
                'description': '认养价格是多因素叠加后的结果',
            }
        ],
    },
    {
        'category': ('成本价格类', 'cost', '围绕养殖投入、阶段成本与价格形成的常见问题'),
        'question': '滩羊价格和月龄有什么关系',
        'answer': '一般来说，月龄越大，饲养周期越长，累计成本越高，价格通常也会更高，但仍要结合体重和市场需求一起判断。',
        'keywords': '滩羊,价格,月龄,关系',
        'aliases': ['月龄越大滩羊越贵吗', '滩羊价格为什么和月龄有关'],
    },
    {
        'category': ('认养流程类', 'adoption', '围绕认养流程、展示与选择方式的常见问题'),
        'question': '认养一只滩羊的流程是什么',
        'answer': '一般流程是先选择心仪羊只或认养方案，完成下单支付后进入认养期，随后可查看羊只信息、成长记录，待达到出栏条件后安排发货或后续处理。',
        'keywords': '认养,流程,怎么认养,步骤',
        'is_hot': True,
        'aliases': ['认养滩羊怎么操作', '认养一只羊需要哪些步骤', '滩羊认养流程是什么'],
        'details': [
            {
                'stage_name': '流程概览',
                'description': '选羊或选方案 -> 下单支付 -> 进入认养期 -> 查看成长信息 -> 出栏发货',
            }
        ],
    },
    {
        'category': ('认养流程类', 'adoption', '围绕认养流程、展示与选择方式的常见问题'),
        'question': '认养后多久能看到我的羊只信息',
        'answer': '通常在认养成功并完成订单确认后，就可以在小程序里查看到自己的羊只信息。若数据同步稍有延迟，一般也会很快更新。',
        'keywords': '认养后,多久,看到,羊只信息',
        'aliases': ['认养成功后什么时候能看到羊', '下单后多久显示我的羊只'],
    },
    {
        'category': ('认养流程类', 'adoption', '围绕认养流程、展示与选择方式的常见问题'),
        'question': '认养时应该怎么选择月龄',
        'answer': '如果更看重性价比和出栏效率，可以优先考虑6个月左右；如果更看重肉质成熟度和风味表现，可以考虑8个月左右。',
        'keywords': '认养,选择,月龄,怎么选',
        'aliases': ['认养滩羊月龄怎么挑', '认养时选6个月还是8个月'],
    },
    {
        'category': ('羊只成长类', 'my_sheep', '围绕认养后羊只成长、记录与状态查看的常见问题'),
        'question': '我的羊现在处于什么阶段',
        'answer': '如果您已登录并完成认养，系统可以结合羊只月龄、体重和记录信息判断当前所处阶段，例如育成期、育肥期或接近出栏阶段。',
        'keywords': '我的羊,现在,什么阶段,成长阶段',
        'aliases': ['我的羊当前到哪个阶段了', '我的羊现在长到哪一步了'],
    },
    {
        'category': ('羊只成长类', 'my_sheep', '围绕认养后羊只成长、记录与状态查看的常见问题'),
        'question': '我的羊最近体重增长情况怎么样',
        'answer': '登录后系统可以结合最近的成长记录，帮您查看羊只近期体重变化趋势，并判断增长是否稳定。',
        'keywords': '我的羊,体重,增长,最近',
        'aliases': ['我的羊最近长了多少斤', '最近体重增长正常吗'],
    },
    {
        'category': ('羊只成长类', 'my_sheep', '围绕认养后羊只成长、记录与状态查看的常见问题'),
        'question': '我的羊最近喂养记录怎么看',
        'answer': '登录后可以查看系统记录的近期喂养信息，包括喂养时间、饲料类型和投喂量等内容。',
        'keywords': '我的羊,喂养记录,怎么看,饲料',
        'aliases': ['我的羊饲喂记录在哪看', '怎么看最近喂了什么'],
    },
    {
        'category': ('羊只成长类', 'my_sheep', '围绕认养后羊只成长、记录与状态查看的常见问题'),
        'question': '我的羊打过哪些疫苗',
        'answer': '登录后系统可以根据疫苗接种记录，查看您的羊只已完成的疫苗名称和接种时间。',
        'keywords': '我的羊,疫苗,打过哪些,免疫记录',
        'aliases': ['我的羊疫苗记录怎么看', '我的羊做过哪些免疫'],
    },
    {
        'category': ('发货履约类', 'delivery', '围绕出栏后发货、物流与履约体验的常见问题'),
        'question': '滩羊出栏后是整只发货还是分割配送',
        'answer': '具体发货形式要以平台当前提供的服务方案为准。通常会根据履约方案安排整只发货或分割配送，用户可在下单或发货前查看说明。',
        'keywords': '出栏后,整只,分割,配送,发货',
        'aliases': ['出栏以后怎么发货', '是整羊发还是分割后发'],
    },
    {
        'category': ('发货履约类', 'delivery', '围绕出栏后发货、物流与履约体验的常见问题'),
        'question': '下单后多久发货',
        'answer': '下单后的发货时间通常取决于当前认养阶段、出栏安排和履约计划。如果是认养类订单，一般要在达到出栏条件后再进入发货流程。',
        'keywords': '下单后,多久发货,发货时间',
        'aliases': ['认养后什么时候发货', '订单多久能发出'],
    },
    {
        'category': ('发货履约类', 'delivery', '围绕出栏后发货、物流与履约体验的常见问题'),
        'question': '发货后物流信息在哪里看',
        'answer': '发货后通常可以在订单详情或相关物流页面查看物流公司、运单信息和配送进度。',
        'keywords': '发货后,物流,在哪里看,订单',
        'aliases': ['物流单号去哪里查', '发货以后怎么看配送进度'],
    },
    {
        'category': ('品种选择类', 'selection', '围绕滩羊特色、选择方式与差异的常见问题'),
        'question': '滩羊和普通羊有什么区别',
        'answer': '滩羊在品种特色、肉质风味、地域品牌和市场认知上都有明显特点，通常更强调风味表现和地域特色价值。',
        'keywords': '滩羊,普通羊,区别,差异',
        'aliases': ['滩羊和别的羊有什么不一样', '为什么要选滩羊'],
    },
    {
        'category': ('品种选择类', 'selection', '围绕滩羊特色、选择方式与差异的常见问题'),
        'question': '公羊和母羊在认养价值上有什么区别',
        'answer': '公羊和母羊在生长节奏、体型表现和认养偏好上可能存在差异，实际选择时建议结合月龄、体况和认养目标综合判断。',
        'keywords': '公羊,母羊,认养价值,区别',
        'aliases': ['认养公羊还是母羊更合适', '公母羊有什么差别'],
    },
]


RELATED_MAP = {
    '滩羊一般多少个月可以出栏': [
        '滩羊6个月可以出栏吗',
        '不同月龄滩羊营养价值有什么区别',
        '滩羊养到6个月成本大概是多少',
        '滩羊价格和月龄有什么关系',
    ],
    '认养一只滩羊的流程是什么': [
        '认养后多久能看到我的羊只信息',
        '认养时应该怎么选择月龄',
        '认养价格怎么计算',
    ],
    '认养价格怎么计算': [
        '滩羊价格和月龄有什么关系',
        '滩羊养到6个月成本大概是多少',
        '认养时应该怎么选择月龄',
    ],
    '我的羊现在处于什么阶段': [
        '我的羊最近体重增长情况怎么样',
        '我的羊最近喂养记录怎么看',
        '我的羊打过哪些疫苗',
    ],
    '我的羊最近体重增长情况怎么样': [
        '我的羊现在处于什么阶段',
        '我的羊最近喂养记录怎么看',
        '我的羊打过哪些疫苗',
    ],
    '下单后多久发货': [
        '发货后物流信息在哪里看',
        '滩羊出栏后是整只发货还是分割配送',
        '认养一只滩羊的流程是什么',
    ],
    '滩羊和普通羊有什么区别': [
        '公羊和母羊在认养价值上有什么区别',
        '不同月龄滩羊营养价值有什么区别',
        '认养时应该怎么选择月龄',
    ],
}


class Command(BaseCommand):
    help = '初始化 FAQ 问答对、别名、结构化详情和关联问题'

    def handle(self, *args, **options):
        qa_map = {}

        for item in FAQ_DATA:
            category_name, category_code, category_desc = item['category']
            category, _ = QACategory.objects.get_or_create(
                code=category_code,
                defaults={
                    'name': category_name,
                    'description': category_desc,
                },
            )
            if category.name != category_name or category.description != category_desc:
                category.name = category_name
                category.description = category_desc
                category.save(update_fields=['name', 'description', 'updated_at'])

            qa_pair, created = QAPair.objects.get_or_create(
                question=item['question'],
                defaults={
                    'category': category,
                    'answer': item['answer'],
                    'keywords': item.get('keywords', ''),
                    'month_stage': item.get('month_stage', ''),
                    'is_hot': item.get('is_hot', False),
                    'status': True,
                },
            )
            if not created:
                qa_pair.category = category
                qa_pair.answer = item['answer']
                qa_pair.keywords = item.get('keywords', '')
                qa_pair.month_stage = item.get('month_stage', '')
                qa_pair.is_hot = item.get('is_hot', False)
                qa_pair.status = True
                qa_pair.save(
                    update_fields=[
                        'category',
                        'answer',
                        'keywords',
                        'month_stage',
                        'is_hot',
                        'status',
                        'updated_at',
                    ]
                )

            qa_pair.aliases.all().delete()
            for alias_question in item.get('aliases', []):
                QAAlias.objects.create(qa_pair=qa_pair, alias_question=alias_question)

            qa_pair.details.all().delete()
            for idx, detail in enumerate(item.get('details', []), start=1):
                QAAnswerDetail.objects.create(
                    qa_pair=qa_pair,
                    stage_name=detail.get('stage_name', ''),
                    weight_range=detail.get('weight_range', ''),
                    nutrition_value=detail.get('nutrition_value', ''),
                    cost_value=detail.get('cost_value', ''),
                    price_value=detail.get('price_value', ''),
                    description=detail.get('description', ''),
                    sort_order=idx,
                )

            qa_map[qa_pair.question] = qa_pair

        QARelated.objects.all().delete()
        for source_question, target_questions in RELATED_MAP.items():
            source_qa = qa_map.get(source_question)
            if not source_qa:
                continue
            for idx, target_question in enumerate(target_questions, start=1):
                target_qa = qa_map.get(target_question)
                if not target_qa:
                    continue
                QARelated.objects.create(
                    source_qa=source_qa,
                    target_qa=target_qa,
                    sort_order=idx,
                )

        self.stdout.write(self.style.SUCCESS(f'FAQ 初始化完成，共处理 {len(qa_map)} 条标准问答。'))
