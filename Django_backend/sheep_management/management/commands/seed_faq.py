import time

from django.core.management.base import BaseCommand
from django.db import OperationalError, close_old_connections

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
        'category': ('出栏周期类', 'shipping_cycle', '围绕滩羊出栏时间与差异的常见问题'),
        'question': '滩羊8个月出栏有什么特点',
        'answer': '8个月左右出栏的滩羊通常肉质更成熟、风味更足，整体食用品质更稳定，但相应的养殖周期更长、投入也更高。',
        'keywords': '滩羊,8个月,出栏,特点,风味',
        'month_stage': '8个月',
        'aliases': ['8个月滩羊出栏怎么样', '八个月出栏的滩羊有什么优势'],
    },
    {
        'category': ('出栏周期类', 'shipping_cycle', '围绕滩羊出栏时间与差异的常见问题'),
        'question': '滩羊几个月口感最好',
        'answer': '如果更看重口感成熟度和羊肉风味，通常8个月左右的滩羊表现更均衡；如果更偏向鲜嫩口感，6个月左右也较受欢迎。',
        'keywords': '滩羊,几个月,口感,最好,风味',
        'aliases': ['滩羊什么时候口感最好', '滩羊几个月吃起来最好'],
    },
    {
        'category': ('出栏周期类', 'shipping_cycle', '围绕滩羊出栏时间与差异的常见问题'),
        'question': '滩羊出栏时间会受季节影响吗',
        'answer': '会。季节变化会影响饲料供给、气候条件和生长节奏，因此实际出栏安排通常会结合季节、体况和市场计划综合判断。',
        'keywords': '滩羊,出栏时间,季节,影响',
        'aliases': ['季节会影响滩羊出栏吗', '滩羊出栏和季节有没有关系'],
    },
    {
        'category': ('出栏周期类', 'shipping_cycle', '围绕滩羊出栏时间与差异的常见问题'),
        'question': '滩羊提前出栏会有什么影响',
        'answer': '如果出栏过早，可能会导致体重积累不足、肉质成熟度不够，整体食用品质和认养价值表现都会受到一定影响。',
        'keywords': '滩羊,提前出栏,影响,体重,肉质',
        'aliases': ['滩羊太早出栏会怎样', '提前出栏会不会影响品质'],
    },
    {
        'category': ('出栏周期类', 'shipping_cycle', '围绕滩羊出栏时间与差异的常见问题'),
        'question': '滩羊延后出栏有什么变化',
        'answer': '延后出栏通常会带来更高的饲养成本，同时肉味会更浓、成熟度更高，但是否值得延后还要看用户需求和成本承受能力。',
        'keywords': '滩羊,延后出栏,变化,成本,风味',
        'aliases': ['滩羊晚一点出栏有什么区别', '延后出栏值不值得'],
    },
    {
        'category': ('出栏周期类', 'shipping_cycle', '围绕滩羊出栏时间与差异的常见问题'),
        'question': '判断滩羊是否适合出栏主要看什么',
        'answer': '一般会综合参考月龄、体重、体况、生长记录和健康状态，而不是只看单一时间点，确保既达到品质要求又符合出栏标准。',
        'keywords': '滩羊,判断,适合出栏,月龄,体重,体况',
        'aliases': ['怎么判断滩羊能不能出栏', '滩羊出栏主要看哪些指标'],
        'details': [
            {
                'stage_name': '综合判断',
                'weight_range': '结合实际体重与体况评估',
                'nutrition_value': '健康稳定时食用品质更有保障',
                'cost_value': '避免过早或过晚出栏带来的成本偏差',
                'price_value': '更有利于维持合理认养价值',
                'description': '月龄、体重、健康和生长曲线通常需要一并参考',
            }
        ],
    },
    {
        'category': ('出栏周期类', 'shipping_cycle', '围绕滩羊出栏时间与差异的常见问题'),
        'question': '同样月龄的滩羊为什么出栏时间不完全一样',
        'answer': '因为不同羊只在生长速度、体重积累、健康状态和饲养条件上会存在差异，所以同样月龄并不一定在同一时间达到理想出栏状态。',
        'keywords': '同样月龄,滩羊,出栏时间,差异',
        'aliases': ['为什么同月龄滩羊出栏时间不同', '同样大为什么有的羊先出栏'],
    },
    {
        'category': ('出栏周期类', 'shipping_cycle', '围绕滩羊出栏时间与差异的常见问题'),
        'question': '认养用户应该选6个月还是8个月出栏',
        'answer': '如果更看重性价比和较快履约，可优先考虑6个月左右；如果更看重风味成熟度和品质体验，则8个月左右通常更合适。',
        'keywords': '认养用户,6个月,8个月,出栏,选择',
        'aliases': ['认养时选6个月出栏还是8个月出栏', '6个月和8个月出栏怎么选'],
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
        'category': ('营养价值类', 'nutrition', '围绕滩羊不同月龄营养与食用品质的问题'),
        'question': '8个月滩羊的营养特点是什么',
        'answer': '8个月滩羊的风味物质更丰富，肉香更明显，整体成熟度更高，适合更看重羊肉层次感和食用品质的人群。',
        'keywords': '滩羊,8个月,营养,特点,风味',
        'month_stage': '8个月',
        'aliases': ['八个月滩羊营养怎么样', '8个月滩羊肉质有什么特点'],
    },
    {
        'category': ('营养价值类', 'nutrition', '围绕滩羊不同月龄营养与食用品质的问题'),
        'question': '滩羊肉蛋白质高吗',
        'answer': '滩羊肉通常富含优质蛋白，适合作为日常膳食中的蛋白质来源之一，同时兼具较好的口感和营养价值。',
        'keywords': '滩羊肉,蛋白质,高吗,营养',
        'aliases': ['滩羊肉蛋白质含量怎么样', '滩羊肉是不是高蛋白'],
    },
    {
        'category': ('营养价值类', 'nutrition', '围绕滩羊不同月龄营养与食用品质的问题'),
        'question': '滩羊肉脂肪含量高不高',
        'answer': '不同月龄和部位的脂肪表现会有差异，整体来看滩羊肉脂肪分布较均衡，既能保留风味，又不会显得过于油腻。',
        'keywords': '滩羊肉,脂肪,含量,高不高',
        'aliases': ['滩羊肉会不会太肥', '滩羊肉脂肪多吗'],
    },
    {
        'category': ('营养价值类', 'nutrition', '围绕滩羊不同月龄营养与食用品质的问题'),
        'question': '滩羊肉适合老人和孩子吃吗',
        'answer': '总体来说适合，但建议根据人群特点选择更合适的月龄和烹饪方式。偏嫩的滩羊更容易咀嚼，清炖等方式也更利于家庭食用。',
        'keywords': '滩羊肉,老人,孩子,适合,食用',
        'aliases': ['老人小孩能吃滩羊肉吗', '滩羊肉适不适合家庭吃'],
    },
    {
        'category': ('营养价值类', 'nutrition', '围绕滩羊不同月龄营养与食用品质的问题'),
        'question': '滩羊肉更适合炖还是烤',
        'answer': '如果偏向鲜嫩口感，清炖更能体现其细腻特点；如果偏向浓郁风味，烧烤或红烧更能突出滩羊的肉香层次。',
        'keywords': '滩羊肉,炖,烤,适合,做法',
        'aliases': ['滩羊肉适合什么做法', '滩羊肉炖着吃还是烤着吃更好'],
    },
    {
        'category': ('营养价值类', 'nutrition', '围绕滩羊不同月龄营养与食用品质的问题'),
        'question': '为什么很多人觉得滩羊肉更鲜嫩',
        'answer': '这通常与品种特性、养殖环境、饲养方式以及月龄控制有关，因此在口感上更容易呈现出细嫩、鲜香的特点。',
        'keywords': '滩羊肉,鲜嫩,原因,品种',
        'aliases': ['滩羊为什么吃起来更嫩', '滩羊肉鲜嫩和什么有关'],
    },
    {
        'category': ('营养价值类', 'nutrition', '围绕滩羊不同月龄营养与食用品质的问题'),
        'question': '滩羊肉的风味和月龄有什么关系',
        'answer': '一般来说，月龄增加后风味会更浓、层次更明显；月龄较小时则更偏向鲜嫩清爽，因此不同月龄更适合不同食用偏好。',
        'keywords': '滩羊肉,风味,月龄,关系',
        'aliases': ['月龄会影响滩羊肉风味吗', '滩羊肉味道和月龄有关吗'],
    },
    {
        'category': ('营养价值类', 'nutrition', '围绕滩羊不同月龄营养与食用品质的问题'),
        'question': '认养时想兼顾营养和口感该怎么选',
        'answer': '如果想兼顾日常营养摄入和良好口感，通常可优先考虑生长较稳定、月龄适中的滩羊，这类羊只在嫩度和风味之间更平衡。',
        'keywords': '认养,营养,口感,怎么选,滩羊',
        'aliases': ['想兼顾营养和口感怎么挑滩羊', '认养时怎么选更均衡'],
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
        'category': ('成本价格类', 'cost', '围绕养殖投入、阶段成本与价格形成的常见问题'),
        'question': '滩羊8个月的养殖成本为什么更高',
        'answer': '8个月滩羊需要更长的饲养周期和持续投入，尤其在饲料、管理和防疫方面会累计更多成本，因此整体价格通常高于6个月阶段。',
        'keywords': '滩羊,8个月,养殖成本,更高,原因',
        'aliases': ['为什么8个月滩羊更贵', '8个月滩羊成本高在哪里'],
    },
    {
        'category': ('成本价格类', 'cost', '围绕养殖投入、阶段成本与价格形成的常见问题'),
        'question': '滩羊成本里哪一部分占比最大',
        'answer': '在多数养殖场景中，饲料投入通常是成本构成中的重要部分，此外防疫、人工和日常管理费用也会持续累积。',
        'keywords': '滩羊,成本构成,饲料,占比,最大',
        'aliases': ['滩羊养殖成本主要花在哪', '滩羊成本最高的是哪部分'],
    },
    {
        'category': ('成本价格类', 'cost', '围绕养殖投入、阶段成本与价格形成的常见问题'),
        'question': '认养价格会不会随着市场波动变化',
        'answer': '会。认养价格除了受月龄和饲养成本影响外，也会参考市场行情、供需变化和平台阶段性安排，因此可能存在一定波动。',
        'keywords': '认养价格,市场波动,变化,行情',
        'aliases': ['认养价格会变动吗', '滩羊认养价会不会受市场影响'],
    },
    {
        'category': ('成本价格类', 'cost', '围绕养殖投入、阶段成本与价格形成的常见问题'),
        'question': '为什么同月龄滩羊价格也会不同',
        'answer': '即便月龄相同，不同羊只的体重、体况、健康状态、性别和成长表现也可能不同，所以价格不一定完全一致。',
        'keywords': '同月龄,滩羊,价格不同,原因',
        'aliases': ['同样月龄为什么价格不一样', '同龄滩羊为什么有贵有便宜'],
    },
    {
        'category': ('成本价格类', 'cost', '围绕养殖投入、阶段成本与价格形成的常见问题'),
        'question': '认养价格里包含后续服务吗',
        'answer': '一般会结合平台提供的服务内容综合确定，例如成长记录展示、认养期管理和履约安排等，具体以平台当期说明为准。',
        'keywords': '认养价格,后续服务,包含,说明',
        'aliases': ['认养价格包不包含服务费', '认养费用里都含什么'],
    },
    {
        'category': ('成本价格类', 'cost', '围绕养殖投入、阶段成本与价格形成的常见问题'),
        'question': '想控制预算应该怎么选择认养方案',
        'answer': '如果预算较敏感，可以优先考虑月龄适中、周转更快的方案，并结合价格区间、月龄和履约周期进行综合选择。',
        'keywords': '预算,认养方案,控制成本,选择',
        'aliases': ['预算有限怎么选认养方案', '想便宜一点应该怎么挑'],
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
        'category': ('认养流程类', 'adoption', '围绕认养流程、展示与选择方式的常见问题'),
        'question': '认养前需要先注册登录吗',
        'answer': '通常需要先完成账号注册与登录，便于系统绑定订单、展示认养记录并在后续提供羊只成长信息和履约服务。',
        'keywords': '认养前,注册,登录,需要吗',
        'aliases': ['认养前是不是要先登录', '下单认养前要不要注册账号'],
    },
    {
        'category': ('认养流程类', 'adoption', '围绕认养流程、展示与选择方式的常见问题'),
        'question': '认养时是选具体羊只还是选方案',
        'answer': '这取决于平台当前提供的模式。有的支持直接挑选具体羊只，有的支持先选认养方案，再由系统展示对应适配对象。',
        'keywords': '认养,具体羊只,方案,选择',
        'aliases': ['认养时能不能自己选羊', '认养是选羊还是选套餐'],
    },
    {
        'category': ('认养流程类', 'adoption', '围绕认养流程、展示与选择方式的常见问题'),
        'question': '认养成功后我还能更换羊只吗',
        'answer': '一般要结合订单状态和平台规则判断。如果订单已经进入认养执行阶段，通常不建议随意更换，具体以平台说明为准。',
        'keywords': '认养成功,更换羊只,可以吗',
        'aliases': ['认养之后还能换羊吗', '下单后能不能改选别的羊'],
    },
    {
        'category': ('认养流程类', 'adoption', '围绕认养流程、展示与选择方式的常见问题'),
        'question': '认养过程中可以看到哪些信息',
        'answer': '通常可查看羊只基础档案、成长记录、饲喂记录、免疫记录以及订单和履约进度等信息，帮助用户持续了解认养状态。',
        'keywords': '认养过程中,看到哪些信息,档案,记录',
        'aliases': ['认养期间能看什么内容', '认养后系统会展示哪些数据'],
    },
    {
        'category': ('认养流程类', 'adoption', '围绕认养流程、展示与选择方式的常见问题'),
        'question': '认养订单支付后下一步是什么',
        'answer': '支付成功后，系统会将订单与用户账号绑定，并进入认养展示和记录跟踪阶段，用户可随后查看自己的羊只档案和成长信息。',
        'keywords': '认养订单,支付后,下一步,绑定',
        'aliases': ['认养付款成功后怎么办', '支付完成后会发生什么'],
    },
    {
        'category': ('认养流程类', 'adoption', '围绕认养流程、展示与选择方式的常见问题'),
        'question': '认养过程中能取消订单吗',
        'answer': '是否可以取消通常取决于订单所处阶段和平台规则。若已进入履约或认养执行阶段，通常需要按照订单政策处理。',
        'keywords': '认养过程,取消订单,可以吗',
        'aliases': ['认养后还能取消吗', '认养订单可以提现吗'],
    },
    {
        'category': ('认养流程类', 'adoption', '围绕认养流程、展示与选择方式的常见问题'),
        'question': '认养流程里优惠券和余额支付怎么用',
        'answer': '在结算阶段通常可以按平台规则选择可用优惠券，并结合余额支付完成下单，系统会自动计算优惠后的实际应付金额。',
        'keywords': '认养流程,优惠券,余额支付,结算',
        'aliases': ['认养时怎么用优惠券', '认养下单能不能余额支付'],
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
        'category': ('羊只成长类', 'my_sheep', '围绕认养后羊只成长、记录与状态查看的常见问题'),
        'question': '我的羊现在健康状态怎么样',
        'answer': '登录后系统可结合羊只档案中的健康状态字段及近期成长、饲喂和免疫记录，帮助您了解当前整体状态是否稳定。',
        'keywords': '我的羊,健康状态,怎么样',
        'aliases': ['我的羊现在健康吗', '怎么看我的羊健康情况'],
    },
    {
        'category': ('羊只成长类', 'my_sheep', '围绕认养后羊只成长、记录与状态查看的常见问题'),
        'question': '我的羊耳标号在哪里看',
        'answer': '登录后可在羊只详情或档案页面查看耳标编号，耳标号通常是识别和追踪羊只的重要标识。',
        'keywords': '我的羊,耳标号,在哪里看,档案',
        'aliases': ['我的羊耳标编号怎么看', '羊只耳标在什么地方显示'],
    },
    {
        'category': ('羊只成长类', 'my_sheep', '围绕认养后羊只成长、记录与状态查看的常见问题'),
        'question': '我的羊最近长高长长了吗',
        'answer': '如果系统已有近期成长记录，您可以查看身高和体长等数据变化，用于辅助判断羊只近期生长是否稳定。',
        'keywords': '我的羊,长高,体长,成长记录',
        'aliases': ['我的羊最近身高体长变化怎么样', '怎么看我的羊最近有没有长大'],
    },
    {
        'category': ('羊只成长类', 'my_sheep', '围绕认养后羊只成长、记录与状态查看的常见问题'),
        'question': '我的羊最近吃的是什么饲料',
        'answer': '系统可依据近期饲喂记录展示投喂时间、饲料类型和数量等内容，帮助您了解羊只最近的喂养情况。',
        'keywords': '我的羊,最近,吃的什么,饲料',
        'aliases': ['我的羊最近喂了什么', '最近给我的羊吃什么饲料'],
    },
    {
        'category': ('羊只成长类', 'my_sheep', '围绕认养后羊只成长、记录与状态查看的常见问题'),
        'question': '我的羊什么时候接近出栏',
        'answer': '系统可结合月龄、体重和阶段记录综合判断羊只是否接近出栏，并帮助用户了解当前所处的大致进度。',
        'keywords': '我的羊,什么时候,接近出栏,进度',
        'aliases': ['我的羊还有多久出栏', '我的羊现在离出栏近吗'],
    },
    {
        'category': ('羊只成长类', 'my_sheep', '围绕认养后羊只成长、记录与状态查看的常见问题'),
        'question': '我的羊为什么暂时看不到新记录',
        'answer': '如果近期没有新增饲喂、成长或免疫记录，或者数据尚在同步处理中，页面上可能暂时看不到新的更新内容。',
        'keywords': '我的羊,看不到新记录,原因,同步',
        'aliases': ['为什么我的羊最近没有更新', '我的羊记录怎么没变化'],
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
        'category': ('发货履约类', 'delivery', '围绕出栏后发货、物流与履约体验的常见问题'),
        'question': '发货前平台会通知我吗',
        'answer': '通常会结合订单状态更新或页面通知提醒用户关注履约进度，具体通知方式以平台当前设计为准。',
        'keywords': '发货前,通知,订单状态,提醒',
        'aliases': ['发货前会不会提醒我', '平台会提前通知发货吗'],
    },
    {
        'category': ('发货履约类', 'delivery', '围绕出栏后发货、物流与履约体验的常见问题'),
        'question': '发货时可以修改收货信息吗',
        'answer': '是否可以修改通常取决于订单所处状态。如果尚未进入实际发货流程，一般更容易处理；若已发货，则通常无法再修改。',
        'keywords': '发货时,修改收货信息,可以吗',
        'aliases': ['发货前能改地址吗', '订单发货前还能改收货人吗'],
    },
    {
        'category': ('发货履约类', 'delivery', '围绕出栏后发货、物流与履约体验的常见问题'),
        'question': '发货后多久能送到',
        'answer': '配送时效通常受物流线路、地区距离和配送方式影响，具体送达时间以物流信息和平台通知为准。',
        'keywords': '发货后,多久送到,时效,物流',
        'aliases': ['发货后几天能到', '滩羊发货一般多久送达'],
    },
    {
        'category': ('发货履约类', 'delivery', '围绕出栏后发货、物流与履约体验的常见问题'),
        'question': '订单显示发货中是什么意思',
        'answer': '这通常表示订单已进入物流履约阶段，相关物流信息正在生成或运输流程已经开始，用户可继续关注订单详情。',
        'keywords': '订单,发货中,是什么意思,履约',
        'aliases': ['订单发货中代表什么', '为什么我的订单显示发货中'],
    },
    {
        'category': ('发货履约类', 'delivery', '围绕出栏后发货、物流与履约体验的常见问题'),
        'question': '订单完成后还能查看物流记录吗',
        'answer': '一般可以在订单详情中查看历史物流信息和履约状态，便于后续追溯和确认配送过程。',
        'keywords': '订单完成,查看物流记录,历史',
        'aliases': ['订单完成后物流信息还在吗', '已完成订单还能看配送记录吗'],
    },
    {
        'category': ('发货履约类', 'delivery', '围绕出栏后发货、物流与履约体验的常见问题'),
        'question': '出栏后到发货之间为什么会有等待时间',
        'answer': '出栏后通常还需要结合履约排期、订单处理、物流安排和发货准备等环节，因此并不一定会立即进入发货状态。',
        'keywords': '出栏后,发货前,等待时间,原因',
        'aliases': ['为什么出栏后还没马上发货', '出栏和发货之间为什么要等'],
    },
    {
        'category': ('发货履约类', 'delivery', '围绕出栏后发货、物流与履约体验的常见问题'),
        'question': '履约完成后订单状态会怎么显示',
        'answer': '履约完成后，订单通常会更新为已完成或相近状态，用户可在订单列表和详情页查看最终状态结果。',
        'keywords': '履约完成,订单状态,显示',
        'aliases': ['发货完成后订单会显示什么', '履约结束后状态怎么变'],
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
    {
        'category': ('品种选择类', 'selection', '围绕滩羊特色、选择方式与差异的常见问题'),
        'question': '选择滩羊时优先看月龄还是体重',
        'answer': '月龄和体重都重要。月龄更能反映成长阶段，体重更能体现当前发育情况，通常需要结合体况一起判断。',
        'keywords': '选择滩羊,月龄,体重,优先看什么',
        'aliases': ['挑滩羊先看月龄还是体重', '选羊时月龄和体重哪个更重要'],
    },
    {
        'category': ('品种选择类', 'selection', '围绕滩羊特色、选择方式与差异的常见问题'),
        'question': '选择滩羊时健康状态重要吗',
        'answer': '非常重要。健康状态会直接影响成长稳定性、履约体验和整体认养价值，因此通常应优先选择状态良好的羊只。',
        'keywords': '选择滩羊,健康状态,重要吗',
        'aliases': ['挑滩羊要不要看健康情况', '选羊时健康状态是不是关键'],
    },
    {
        'category': ('品种选择类', 'selection', '围绕滩羊特色、选择方式与差异的常见问题'),
        'question': '第一次认养滩羊怎么挑更合适',
        'answer': '第一次认养通常建议优先选择信息完整、记录清晰、月龄适中且状态稳定的羊只，这样更便于理解认养过程和后续跟踪。',
        'keywords': '第一次认养,滩羊,怎么挑,合适',
        'aliases': ['新手认养滩羊怎么选', '第一次挑滩羊有什么建议'],
    },
    {
        'category': ('品种选择类', 'selection', '围绕滩羊特色、选择方式与差异的常见问题'),
        'question': '滩羊月龄不同适合哪些人群',
        'answer': '偏小月龄通常更适合看重性价比和鲜嫩口感的人群，偏大月龄则更适合看重风味成熟度和品质层次的人群。',
        'keywords': '滩羊,月龄不同,适合人群',
        'aliases': ['不同月龄滩羊适合谁', '6个月和8个月滩羊分别适合什么人'],
    },
    {
        'category': ('品种选择类', 'selection', '围绕滩羊特色、选择方式与差异的常见问题'),
        'question': '挑选滩羊时耳标号有什么作用',
        'answer': '耳标号是羊只的重要身份标识，可用于档案追踪、记录关联和个体区分，也是认养透明化管理的重要依据。',
        'keywords': '挑选滩羊,耳标号,作用',
        'aliases': ['选羊时耳标有什么用', '为什么挑羊要看耳标编号'],
    },
    {
        'category': ('品种选择类', 'selection', '围绕滩羊特色、选择方式与差异的常见问题'),
        'question': '滩羊为什么更适合做认养展示',
        'answer': '滩羊具有较强的地域特色和品种辨识度，加上成长过程和履约路径较容易数字化展示，因此更适合做认养型场景展示。',
        'keywords': '滩羊,认养展示,适合,原因',
        'aliases': ['为什么认养平台喜欢用滩羊', '滩羊适合线上认养展示吗'],
    },
    {
        'category': ('品种选择类', 'selection', '围绕滩羊特色、选择方式与差异的常见问题'),
        'question': '挑选滩羊时体型和体况怎么看',
        'answer': '通常可结合体重、身高、体长和健康状态综合判断。体型匀称、体况稳定、记录完整的羊只往往更适合作为认养对象。',
        'keywords': '挑选滩羊,体型,体况,怎么看',
        'aliases': ['选滩羊时怎么看体型', '认养时怎么判断羊只体况好不好'],
    },
    {
        'category': ('品种选择类', 'selection', '围绕滩羊特色、选择方式与差异的常见问题'),
        'question': '如果更看重风味应该怎么选滩羊',
        'answer': '如果更看重风味层次和成熟度，通常可以优先考虑月龄稍大、体况稳定、成长记录较完整的羊只。',
        'keywords': '风味,怎么选,滩羊,月龄',
        'aliases': ['重视口感风味怎么挑滩羊', '想吃起来更香应该选哪种滩羊'],
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

    @staticmethod
    def with_db_retry(func, retries=3, delay=1.0):
        last_error = None
        for attempt in range(retries):
            try:
                close_old_connections()
                return func()
            except OperationalError as exc:
                last_error = exc
                if attempt == retries - 1:
                    raise
                time.sleep(delay * (attempt + 1))
        raise last_error

    def handle(self, *args, **options):
        qa_map = {}

        for item in FAQ_DATA:
            category_name, category_code, category_desc = item['category']
            category, _ = self.with_db_retry(
                lambda: QACategory.objects.get_or_create(
                    code=category_code,
                    defaults={
                        'name': category_name,
                        'description': category_desc,
                    },
                )
            )
            if category.name != category_name or category.description != category_desc:
                category.name = category_name
                category.description = category_desc
                self.with_db_retry(
                    lambda: category.save(update_fields=['name', 'description', 'updated_at'])
                )

            qa_pair, created = self.with_db_retry(
                lambda: QAPair.objects.get_or_create(
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
            )
            if not created:
                qa_pair.category = category
                qa_pair.answer = item['answer']
                qa_pair.keywords = item.get('keywords', '')
                qa_pair.month_stage = item.get('month_stage', '')
                qa_pair.is_hot = item.get('is_hot', False)
                qa_pair.status = True
                self.with_db_retry(
                    lambda: qa_pair.save(
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
                )

            self.with_db_retry(lambda: qa_pair.aliases.all().delete())
            for alias_question in item.get('aliases', []):
                self.with_db_retry(
                    lambda alias_question=alias_question: QAAlias.objects.create(
                        qa_pair=qa_pair, alias_question=alias_question
                    )
                )

            self.with_db_retry(lambda: qa_pair.details.all().delete())
            for idx, detail in enumerate(item.get('details', []), start=1):
                self.with_db_retry(
                    lambda idx=idx, detail=detail: QAAnswerDetail.objects.create(
                        qa_pair=qa_pair,
                        stage_name=detail.get('stage_name', ''),
                        weight_range=detail.get('weight_range', ''),
                        nutrition_value=detail.get('nutrition_value', ''),
                        cost_value=detail.get('cost_value', ''),
                        price_value=detail.get('price_value', ''),
                        description=detail.get('description', ''),
                        sort_order=idx,
                    )
                )

            qa_map[qa_pair.question] = qa_pair

        self.with_db_retry(lambda: QARelated.objects.all().delete())
        for source_question, target_questions in RELATED_MAP.items():
            source_qa = qa_map.get(source_question)
            if not source_qa:
                continue
            for idx, target_question in enumerate(target_questions, start=1):
                target_qa = qa_map.get(target_question)
                if not target_qa:
                    continue
                self.with_db_retry(
                    lambda idx=idx, source_qa=source_qa, target_qa=target_qa: QARelated.objects.create(
                        source_qa=source_qa,
                        target_qa=target_qa,
                        sort_order=idx,
                    )
                )

        self.stdout.write(self.style.SUCCESS(f'FAQ 初始化完成，共处理 {len(qa_map)} 条标准问答。'))
