from langchain import LLMChain, PromptTemplate
from langchain.llms import BaseLLM
from pydantic import BaseModel, Field
from langchain.chains.base import Chain


class AgentConversationChain(LLMChain):
    """Chain para gerar a próxima frase da conversação."""

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        sales_agent_inception_prompt = (
        """Nunca esqueça, seu nome é {salesperson_name}. Você trabalha como {salesperson_role}.
        Você trabalha na empresa chamada {company_name}. O negócio da empresa {company_name} é o seguinte: {company_business}
        Os valores da empresa são os seguintes: {company_values}
        Vocês está contatando um potencial cliente para {conversation_purpose}
        Seu meio de contato para o prospect é {conversation_type}

        Se você for perguntado onde conseguiu a informação de contato do usuário, diga que obteve em dados públicos.
        Mantenha suas respostas curtas para reter a atenção do usuário. Nunca produza listas, apenas respostas.
        Você deve responder de acordo com o histórico da conversa e o estágio da conversa em que você está.
        Apenas gere uma resposta por vez! Quando terminar de gerar, termine com '<END_OF_TURN>' para dar uma chance para o usuário responder.
        Exemplo:
        Histórico de conversa:
        {salesperson_name}: Oi, como você está? Me chamo {salesperson_name}, trabalho para a {company_name}. Você tem um minuto? <END_OF_TURN>
        User: Estou bem, e sim. Porque você está ligando? <END_OF_TURN>
        {salesperson_name}:
        Fim do exemplo.

        Estágio atual da conversa:
        {conversation_stage}
        Histórico de conversa:
        {conversation_history}
        {salesperson_name}:
        """
        )
        prompt = PromptTemplate(
            template=sales_agent_inception_prompt,
            input_variables=[
                "salesperson_name",
                "salesperson_role",
                "company_name",
                "company_business",
                "company_values",
                "conversation_purpose",
                "conversation_type",
                "conversation_stage",
                "conversation_history"
            ],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)