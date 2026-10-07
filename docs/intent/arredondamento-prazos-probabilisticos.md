# Declaração Confirmada de Intenção (Statement of Intent)

**Tópico:** Arredondamento Estrito para Cima (\math.ceil\) em Prazos e Lead Times Probabilísticos da GCC e Telebras  
**Data de Confirmação:** 2026-09-27  
**Status:** Confirmado pelo Usuário  

---

## 1. Declaração de Intenção

* **Objetivo (Outcome):** Arredondar estritamente para cima (\math.ceil\) todos os cálculos e exibições de dias úteis e prazos de entrega (tramitação GCC, cenários otimista/esperado/pessimista e lead time total até o local), garantindo números inteiros sem decimais nas telas e no calendário.
* **Usuário Beneficiário (User):** Servidores demandantes, Diretorias e analistas da GCC da Telebras que planejam e acompanham as previsões de recebimento de materiais e serviços.
* **Motivação (Why now):** Eliminar frações de dias (como 30,4 ou 8,5 dias) que causam ambiguidade operacional no cronograma de contratação.
* **Critério de Sucesso (Success):** 100% dos prazos exibidos em dias úteis e somados no calendário constam como números inteiros pelo teto de segurança operacional (\math.ceil\), sem qualquer fração em cards, badges, formulários e retornos de API.
* **Restrição Vinculante (Constraint):** O arredondamento para cima (\math.ceil\) é restrito às contagens de dias úteis e prazos de entrega; métricas de auditoria estatística (margem de erro $\le 2,0\%$ e desvio padrão $\sigma$) mantêm sua precisão decimal.
* **Fora de Escopo (Out of Scope):** Modificar as fórmulas fundamentais do modelo estatístico (distribuição PERT Beta $\mu = \frac{a + 4m + b}{6}$,  = 2,576$ e Grau de Confiança de 99%).
