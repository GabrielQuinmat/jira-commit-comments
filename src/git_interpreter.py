from rich.logging import RichHandler
import logging
from langchain_community.document_loaders import JSONLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from git_loader import GitDocumentLoader

from dotenv import load_dotenv
import os


class GitInterpreter:
    SUMMARIZE_TEMPLATE = """Summarize the changes made in this commit. {text}
    CONCISE SUMMARY:"""
    REFINE_TEMPLATE = (
        'Your job is to produce a final summary of the work done given some commit data.' 
        'Generate the text as a comment that will be posted in a Jira Issue.'
        'Act as you were the developer and you will post your work of the day.'
        'Don\'t provide specific dates or hours, neither path of the files.'
        'Just summarize at a global level what was the main change.\n'
        'If the amount of changes is too big, you can summarize the main changes using a paragraph.\n'
        'We have provided an existing summary up to a certain point: {existing_answer}\n'
        'We have the opportunity to refine the existing summary'
        '(only if needed) with some more context below.\n'
        '------------\n'
        '{text}\n'
        '------------\n'
        'Given the new context, refine the original summary'
        "If the context isn't useful, return the original summary."
    )

    def __init__(self, json_path, verbose=False) -> None:
        load_dotenv()
        FORMAT = '%(message)s'
        if verbose:
            logging.basicConfig(
                level='DEBUG', format=FORMAT, datefmt='[%X]', handlers=[RichHandler()]
            )
        else:
            logging.basicConfig(
                level='INFO', format=FORMAT, datefmt='[%X]', handlers=[RichHandler()]
            )
        self.log = logging.getLogger('rich')
        self.llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), model='gpt-4-turbo', temperature=0.3)
        self.loader = GitDocumentLoader(file_path=json_path)
        self.json_path = json_path
        self.prompt = PromptTemplate.from_template(self.SUMMARIZE_TEMPLATE)
        self.refine_prompt = PromptTemplate.from_template(self.REFINE_TEMPLATE)

    def interpret_commits(self):
        try:
            docs = self.loader.load()
            if not docs:
                return -1
            chain = load_summarize_chain(
                llm=self.llm,
                chain_type='refine',
                question_prompt=self.prompt,
                refine_prompt=self.refine_prompt,
                return_intermediate_steps=True,
                input_key='input_documents',
                output_key='output_text',
            )
            result = chain({'input_documents': docs}, return_only_outputs=True)
            return result["output_text"]
        except Exception as e:
            self.log.error(e)
            return -1
