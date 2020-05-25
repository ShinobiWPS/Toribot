# Toribot

## Install

`pip install -r requirements.txt`

---

## Variabili principali

- **valore_acquisto** = prezzo di acquisto ripple
- **valore_attuale** = prezzo nuovo arrivato
- **ultimo_valore** = prezzo precedente

---

## Spiegazione richieste Bitstamp

1 balance - per controllare se abbiamo asset per fare il necessario
2 order status - se l'ordine e' completato oppure non esiste,prosegui,altrimenti se e' Open, non fare make-order
3 make order - crea l'ordine

---

## Glossario

- **asset** = insieme di beni da utilizzare per il commercio (euro,xrp,btc,petrolio,azioni, burro,mais,ecc)
- **order** = ordine (ambivalente, di acquisto o vendita)
- **trade** = 2 order si soddisfano a vicenda,i 2 commercianti si scambiano gli asset dell order
- **all-in** = esegui un trade usando tutti gli asset (vendi o compra tutto)
- **split**/**splitted** = esegui un trade usando una parte degli asset (vendi o compra una parte)

## Strategie di commercio

- #### Binaria (B)
  ![alt text](B.png)
- #### Binaria con Rischio (BR)

  > Come la B ma essa accetta un CAP di perdita per evitare di rimanere in attesa di un guadagno certo riducendo difatto il guadagno perche fermo


      		- 	BR_Fattore_Approssimazionoe = 8
      		- 	BR_Fattore_Perdita = -0.01
      		- 	FEE = 0.5

- #### Montagna (M)

  ![alt text](M.png)

  ### --Modificatori--

  - Approssimazione (1o decimale, 2o decimale, 3o decimale,ecc)

---

## Accorgimenti

- maggiore la fee, maggiore il tempo da prendere in considerazione (per giocare sul realtime/minuto servirebbe qualcosa non superiore al 0.1% per trade)

---

## VSCode

- il file .env con il vscode workspace.json sono necessari solo temporaneamente per ovviare al bug di intelliCode (a volte mostra import irrisolti, ma sono falsi negativi) perche usa una preview di Microsoft Python Language Analisys
