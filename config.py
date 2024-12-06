GRAPH_TEMPLATE = {
    '相关部门': {
         'slots': ['相关部门'],
         'question': '风暴潮来临，%相关部门%应该采取哪些措施？',
         'cypher': "MATCH (n:相关部门)-[:责任关系]->(m) WHERE n.name='%相关部门%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + '、' + x), 1) AS RES",
         'answer': '【%相关部门%】负责职能：%RES%',
    },
    '组织体系': {
        'slots': ['组织体系'],
        'question': '面对风暴潮灾害时，%组织体系%应该由哪些部门构成？',
        'cypher': "MATCH (n:组织体系)-[:组成关系]->(m) WHERE n.name='%组织体系%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + '、' + x), 1) AS RES",
        'answer': '【%组织体系%】构成：%RES%'
    },
    '组织体系': {
        'slots': ['组织体系'],
        'question': '面对风暴潮灾害时，%组织体系%可以采取哪些措施？',
        'cypher': "MATCH (n:组织体系)-[:责任关系]->(m) WHERE n.name='%组织体系%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + '、' + x), 1) AS RES",
        'answer': '【%组织体系%】可以采取的措施：%RES%'
    },
     '灾害信息': {
        'slots': ['灾害信息'],
        'question': '风暴潮灾害中，%灾害信息%有哪些？',
        'cypher': "MATCH (n:灾害信息)-[r:所有关系|组成关系]->(m) WHERE n.name='%灾害信息%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + '、' + x), 1) AS RES",
        'answer': '风暴潮灾害中【%灾害信息%】有：%RES%'
    },
     '保障措施': {
        'slots': ['保障措施'],
        'question': '面对自然灾害时，%保障措施%可以包含哪些种类？',
        'cypher': "MATCH (a:预案)-[:所有关系]->(b:保障措施) RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(b.name) | s + '、' + x), 1) AS RES;",
        'answer': '【%保障措施%】种类：%RES%'
    },
     '保障措施': {
        'slots': ['保障措施'],
        'question': '发生自然灾害时，%保障措施%有哪些内容？',
        'cypher': "MATCH (n:保障措施)-[:所有关系]-(c:保障措施内容) WHERE n.name='%保障措施%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(c.name) | s + '、' + x), 1) AS RES;",
        'answer': '发生灾害时，【%保障措施%】内容有：%RES%'
    },
    '运行机制': {
        'slots': ['运行机制'],
        'question': '发生自然灾害时，%运行机制%有哪些内容？',
        'cypher': "MATCH (n:运行机制)-[:所有关系]-(c:基本任务) WHERE n.name='%运行机制%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(c.name) | s + '、' + x), 1) AS RES;",
        'answer': '发生灾害时，【%运行机制%】内容有：%RES%'
    },
    '工作小组': {
        'slots': ['工作小组'],
        'question': '应对风暴潮灾害时，可以形成哪些%工作小组%？',
        'cypher': "MATCH (n:工作小组) RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(n.name) | s + '、' + x), 1) AS RES;",
        'answer': '【%工作小组%】有：%RES%'
    },
    '工作小组': {
        'slots': ['工作小组'],
        'question': '应对风暴潮灾害时，%工作小组%有哪些任务？',
        'cypher': "MATCH (n:工作小组)-[:责任关系]-(c:基本任务) WHERE n.name='%工作小组%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(c.name) | s + '、' + x), 1) AS RES;",
        'answer': '【%工作小组%】的任务有：%RES%'
    },
    '工作人员': {
        "slots": ["工作人员"],
        "question": "应对风暴潮灾害时，%工作人员%有哪些基本任务或响应任务？",
        "cypher": "MATCH (n:工作人员)-[:责任关系]->(c) WHERE n.name='%工作人员%' AND (c:基本任务 OR c:响应任务) RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(c.name) | s + '、' + x), 1) AS RES;;",
        "answer": "【%工作人员%】的基本任务或响应任务有：% RES%"
    },
    '响应等级': {
        "slots": ["响应等级"],
        "question": "发生风暴潮时，%响应等级%灾害对应的响应内容有哪些?",
        "cypher": "MATCH (n:响应等级)-[:响应内容]->(m) WHERE n.name='%响应等级%' RETURN SUBSTRING (REDUCE (s = '', x IN COLLECT (m.name) | s + '、' + x), 1) AS RES;",
        "answer": "【%响应等级%】对应的响应内容有：%RES%"
    },
    '响应等级':{
      "slots": ["响应等级"],
      "question": "风暴潮灾害的严重程度%响应等级%怎么定义的？",
      "cypher": "MATCH (n:响应等级)-[:所有关系]-(c:事件) WHERE n.name='%响应等级%' RETURN SUBSTRING (REDUCE (s = '', x IN COLLECT (c.name) | s + '、' + x), 1) AS RES;",
      "answer": "【%响应等级%】相关的事件有：%RES%"
    },
    '事件':{
      "slots": ["事件"],
      "question": "事件描述：%事件%，它对应的响应等级是什么？",
      "cypher": "MATCH (n:事件)-[:响应关系]-(c:响应等级) WHERE n.name='%事件%' RETURN SUBSTRING (REDUCE (s = '', x IN COLLECT (c.name) | s + '、' + x), 1) AS RES;",
      "answer": "【%事件%】的响应等级是：%RES%"
    },
    '事件':{
      "slots": ["事件"],
      "question": "事件描述：%事件%，它对应的处置措施是什么？",
      "cypher": "MATCH (n:事件)-[:响应关系]-(c:基本任务) WHERE n.name='%事件%' RETURN SUBSTRING (REDUCE (s = '', x IN COLLECT (c.name) | s + '、' + x), 1) AS RES;",
      "answer": "【%事件%】的处置措施是：%RES%"
    },

}