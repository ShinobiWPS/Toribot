# Toribot

## Variabili principali

- **valore_acquisto** = prezzo di acquisto ripple
- **valore_attuale** = prezzo nuovo arrivato
- **ultimo_valore** = prezzo precedente

---

## Glossario

- **asset** = insieme di beni da utilizzare per il commercio (euro,xrp,btc,petrolio,azioni, burro,mais,ecc)
- **order** = ordine (ambivalente, di acquisto o vendita)
- **trade** = 2 order si soddisfano a vicenda,i 2 commercianti si scambiano gli asset dell order
- **all-in** = esegui un trade usando tutti gli asset (vendi o compra tutto)
- **split**/**splitted** = esegui un trade usando una parte degli asset (vendi o compra una parte)

## Strategie di commercio

- #### Binaria Senza Approssimazione (BSA)
  ![alt text](BSA.png)
- #### Montagna (M)
  ![alt text](montagna.png)
- ### _Binaria Approssimata (BA) - manca spiegazione_

---

## VSCode

- il file .env con il vscode workspace.json sono necessari solo temporaneamente per ovviare al bug di intelliCode (a volte mostra import irrisolti, ma sono falsi negativi) perche usa una preview di Microsoft Python Language Analisys
