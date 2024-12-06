import shutup
shutup.please()

import gradio as gr
from service import Service

def QA_bot(message, history):
    service = Service()
    return service.answer(message, history)





css = '''
.gradio-container { max-width:850px !important; margin:20px auto !important;}
.message { padding: 10px !important; font-size: 14px !important;}
'''

demo = gr.ChatInterface(
    css=css,
    fn=QA_bot,
    title='海洋风暴潮智能问答机器人',
    chatbot=gr.Chatbot(height=700, bubble_full_width=False),
    theme=gr.themes.Default(spacing_size='sm', radius_size='sm'),
    textbox=gr.Textbox(placeholder="在此输入您的问题", container=False, scale=9),
    examples=[
        '你好',
        '师大维智是什么公司',
        '风暴潮来临，哪些部门应该采取措施？',
        '风暴潮来临，应该采取哪些措施？',
    ],
    submit_btn=gr.Button('提交', variant='primary'),
    clear_btn=gr.Button('清空记录'),
    retry_btn=None,
    undo_btn=None,
)


# -------------旧版---------------------

#css = '''
#.gradio-container { max-width:850px !important; margin:20px auto !important;}
#.message { padding: 10px !important; font-size: 14px !important;}
#'''

# demo = gr.ChatInterface(
#     css = css,
#     fn = doctor_bot,
#     title = '医疗问诊机器人',
#     chatbot = gr.Chatbot(height=700, bubble_full_width=False),   # height=400
#     theme = gr.themes.Default(spacing_size='sm', radius_size='sm'),
#     textbox=gr.Textbox(placeholder="在此输入您的问题", container=False, scale=9), # scale=7
#     examples = ['你好，你叫什么名字？', '寻医问药网获得过哪些投资？', '寻医问药网获的客服电话是多少？', '鼻炎是一种什么病？', '一般会有哪些症状？', '吃什么药好得快？可以吃阿莫西林吗？', '刀郎最近有什么新专辑？'],
#     submit_btn = gr.Button('提交', variant='primary'),
#     clear_btn = gr.Button('清空记录'),
#     retry_btn = None,
#     undo_btn = None,
# )

if __name__ == '__main__':
    demo.launch(share=False)