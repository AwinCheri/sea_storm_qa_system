from utils import *
from config import *
from prompt import *

import os
from langchain.chains import LLMChain, LLMRequestsChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores.chroma import Chroma
from langchain.vectorstores.faiss import FAISS
from langchain.schema import Document
from langchain.agents import ZeroShotAgent, AgentExecutor, Tool, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain import hub


def generic_func(x, query):
    prompt = PromptTemplate.from_template(GENERIC_PROMPT_TPL)
    llm_chain = LLMChain(
        llm = get_llm_model(),
        prompt = prompt,
        verbose = os.getenv('VERBOSE')
    )
    return llm_chain.invoke(query)['text']


class Agent():
    def __init__(self):
        self.vdb = Chroma(
            persist_directory = os.path.join(os.path.dirname(__file__), './data/db'), 
            embedding_function = get_embeddings_model()
        )

    def retrival_func(self, x, query):
        # 召回并过滤文档
        documents = self.vdb.similarity_search_with_relevance_scores(query, k=5)
        query_result = [doc[0].page_content for doc in documents if doc[1]>0.7]

        # 填充提示词并总结答案
        prompt = PromptTemplate.from_template(RETRIVAL_PROMPT_TPL)
        retrival_chain = LLMChain(
            llm = get_llm_model(),
            prompt = prompt,
            verbose = os.getenv('VERBOSE')
        )
        inputs = {
            'query': query,
            'query_result': '\n\n'.join(query_result) if len(query_result) else '没有查到'
        }
        return retrival_chain.invoke(inputs)['text']

    def graph_func(self, x, query):
        # 命名实体识别
        response_schemas = [
            ResponseSchema(type='list', name='相关部门', description='相关部门名称实体'),
            ResponseSchema(type='list', name='灾害信息', description='灾害信息名称实体,例如：灾情情况、灾害预警信息、信息等'),
            ResponseSchema(type='list', name='组织体系', description='组织体系名称实体'),
            ResponseSchema(type='list', name='保障措施', description='保障措施名称实体，例如:资金保障、人力保障等'),
            ResponseSchema(type='list', name='运行机制', description='运行机制名称实体，包括：处置措施、应急处置、后期处置、信息发布、灾情报告、恢复重建、先期处置等等'),
            ResponseSchema(type='list', name='工作小组', description='工作小组名称实体，包括：综合协调组、综合救援组、物资保障组、工程抢险组等等'),
            ResponseSchema(type='list', name='工作人员', description='工作人员名称实体，包括市减灾委主任、副总指挥、市委市政府主要领导等等'),
            ResponseSchema(type='list', name='响应等级', description='响应等级名称实体，包括Ⅰ级、Ⅳ级、重大、一般等等'),
            ResponseSchema(type='list', name='事件', description='对某件事情的描述'),
        ]

        output_parser = StructuredOutputParser(response_schemas=response_schemas)
        format_instructions = structured_output_parser(response_schemas)

        ner_prompt = PromptTemplate(
            template = NER_PROMPT_TPL,
            partial_variables = {'format_instructions': format_instructions},
            input_variables = ['query']
        )

        ner_chain = LLMChain(
            llm = get_llm_model(),
            prompt = ner_prompt,
            verbose = os.getenv('VERBOSE')
        )

        result = ner_chain.invoke({
            'query': query
        })['text']
        
        ner_result = output_parser.parse(result)
        print("提问问句为:"+ query)
        print("实体抽取结果:"+str(ner_result))

        # 命名实体识别结果，填充模板
        graph_templates = []
        for key, template in GRAPH_TEMPLATE.items():
            slot = template['slots'][0]
            slot_values = ner_result[slot]
            for value in slot_values:
                graph_templates.append({
                    'question': replace_token_in_string(template['question'], [[slot, value]]),
                    'cypher': replace_token_in_string(template['cypher'], [[slot, value]]),
                    'answer': replace_token_in_string(template['answer'], [[slot, value]]),
                })
        if not graph_templates:
            return 
        
        # 计算问题相似度，筛选最相关问题
        graph_documents = [
            Document(page_content=template['question'], metadata=template)
            for template in graph_templates
        ]
        db = FAISS.from_documents(graph_documents, get_embeddings_model())
        graph_documents_filter = db.similarity_search_with_relevance_scores(query, k=5)
        print(graph_documents_filter)

        # 执行CQL，拿到结果
        query_result = []
        neo4j_conn = get_neo4j_conn()
        for document in graph_documents_filter:
            question = document[0].page_content
            cypher = document[0].metadata['cypher']
            answer = document[0].metadata['answer']
            try:
                result = neo4j_conn.run(cypher).data()
                if result and any(value for value in result[0].values()):
                    answer_str = replace_token_in_string(answer, list(result[0].items()))
                    query_result.append(f'问题：{question}\n答案：{answer_str}')
            except:
                pass
        print(query_result)
            
        # 总结答案
        prompt = PromptTemplate.from_template(GRAPH_PROMPT_TPL)
        graph_chain = LLMChain(
            llm = get_llm_model(),
            prompt = prompt,
            verbose = os.getenv('VERBOSE')
        )
        inputs = {
            'query': query,
            'query_result': '\n\n'.join(query_result) if len(query_result) else '没有查到'
        }
        return graph_chain.invoke(inputs)['text']
        
    def search_func(self, query):
        prompt = PromptTemplate.from_template(SEARCH_PROMPT_TPL)
        llm_chain = LLMChain(
            llm = get_llm_model(),
            prompt = prompt,
            verbose = os.getenv('VERBOSE')
        )
        llm_request_chain = LLMRequestsChain(
            llm_chain = llm_chain,
            requests_key = 'query_result'
        )
        inputs = {
            'query': query,
            'url': 'https://www.so.com/s?q='+query.replace(' ', '+')
        }
        return llm_request_chain.invoke(inputs)['output']

    def parse_tools(self, tools, query):
        prompt = PromptTemplate.from_template(PARSE_TOOLS_PROMPT_TPL)
        llm_chain = LLMChain(
            llm = get_llm_model(),
            prompt = prompt,
            verbose = os.getenv('VERBOSE')
        )
        # 拼接工具描述参数
        tools_description = ''
        for tool in tools:
            tools_description += tool.name + ':' + tool.description + '\n'
        result = llm_chain.invoke({'tools_description':tools_description, 'query':query})
        # 解析工具函数
        for tool in tools:
            if tool.name == result['text']:
                return tool
        return tools[0]

    def query(self, query):
        tools = [
            Tool.from_function(
                name = 'generic_func',
                func = lambda x: generic_func(x, query),
                description = '可以解答通用领域的知识，例如打招呼，问你是谁等问题',
            ),
            Tool.from_function(
                name = 'retrival_func',
                func = lambda x: self.retrival_func(x, query),
                description = '用于回答文档的相关问题',
            ),
            Tool(
                name = 'graph_func',
                func = lambda x: self.graph_func(x, query),
                description = '用于回答关于海洋风暴潮的相关问题',
            ),
            Tool(
                name = 'search_func',
                func = self.search_func,
                description = '其他工具没有正确答案时，通过搜索引擎，回答通用类问题',
            ),
        ]
        tool = self.parse_tools(tools, query)
        return tool.func(query)

        # prefix = """请用中文，尽你所能回答以下问题。您可以使用以下工具："""
        # suffix = """Begin!

        # History: {chat_history}
        # Question: {input}
        # Thought:{agent_scratchpad}"""

        # agent_prompt = ZeroShotAgent.create_prompt(
        #     tools=tools,
        #     prefix=prefix,
        #     suffix=suffix,
        #     input_variables=['input', 'agent_scratchpad', 'chat_history']
        # )
        # llm_chain = LLMChain(llm=get_llm_model(), prompt=agent_prompt)
        # agent = ZeroShotAgent(llm_chain=llm_chain)

        # memory = ConversationBufferMemory(memory_key='chat_history')
        # agent_chain = AgentExecutor.from_agent_and_tools(
        #     agent = agent, 
        #     tools = tools, 
        #     memory = memory, 
        #     verbose = os.getenv('VERBOSE')
        # )
        # return agent_chain.run({'input': query})

        # prompt = hub.pull('hwchase17/react-chat')
        prompt = PromptTemplate.from_template(REACT_CHAT_PROMPT_TPL)
        prompt.template = '请用中文回答问题！Final Answer 必须尊重 Obversion 的结果，不能改变语义。\n\n' + prompt.template
        agent = create_react_agent(llm=get_llm_model(), tools=tools, prompt=prompt)
        memory = ConversationBufferMemory(memory_key='chat_history')
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent = agent, 
            tools = tools, 
            memory = memory, 
            handle_parsing_errors = True,
            verbose = os.getenv('VERBOSE')
        )
        return agent_executor.invoke({"input": query})['output']


if __name__ == '__main__':
    agent = Agent()

    # print(agent.query('你好'))
    # print(agent.query('寻医问药网获得过哪些投资？'))
    # print(agent.query('鼻炎和感冒是并发症吗？'))
    # print(agent.query('鼻炎怎么治疗？'))
    # print(agent.query('烧橙子可以治感冒吗？'))


    # print(agent.generic_func('', '你好'))
    # print(agent.generic_func('你叫什么名字？'))

    # print(agent.retrival_func('介绍一下寻医问药网'))
    # print(agent.retrival_func('寻医问药网的客服电话是多少？'))

    # print(agent.graph_func('','风暴潮来临，区应急管理局应该采取什么措施'))
    #rint(agent.graph_func('','应对风暴潮灾害的时候，成立一个市减灾委该由哪些部门组成'))
    #print(agent.graph_func('','风暴潮灾害中，灾情情况有哪些'))
    #print(agent.graph_func('','风暴潮灾害中，具体的灾情情况有哪些'))
    #print(agent.graph_func('', '面对自然灾害时，保障措施可以包含哪些种类'))
    #print(agent.graph_func('', '面对海洋风暴潮时，广州市安保预案的人力保障措施应当有哪些内容'))
    #print(agent.graph_func('', '发生台风时，有关部门的先期处置该怎么做？'))
    print(agent.graph_func('', '发生风暴潮时，可以组成哪些工作小组来应对灾害？'))
    #print(agent.graph_func('', '应对风暴潮灾害时，综合协调组有哪些任务？'))
    #print(agent.graph_func('', '风暴潮灾害的严重程度重大怎么定义的？'))
    #print(agent.graph_func('', '发生风暴潮时，发生Ⅳ级灾害对应的响应内容有哪些?'))
    #print(agent.graph_func('', '风暴潮来临时，市减灾委可以采取哪些措施，组织体系为：市减灾委'))

    #print(agent.graph_func('', '预计未来24小时有强台风以上级别的热带气旋登陆我省，这个事件对应的响应等级是？'))# #print(agent.graph_func('', '事件描述：文化市场经营设施、设备遭到破坏，造成恶劣社会影响的突发事件发生，它对应的处置措施是什么？'))
