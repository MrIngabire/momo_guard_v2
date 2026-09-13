"""
Extended SMS training corpus for MoMo Guard.
Labels: 1 = scam/smishing, 0 = legitimate.
Languages: Kinyarwanda, English, French, and mixed.
Scope: P2P, MoMoPay, Bank integrations, MoKash, Utilities, Phishing, Fake Receipts, USSD Injections, Impersonation.
"""

TRAINING_DATA = [
    # ==========================================
    # 🔴 SCAMS & SMISHING (Label = 1)
    # ==========================================

    # -- 1. Fake MoMo Receipts (Spoofed texts from regular numbers) --
    ("Transaction ID: 198426749. You have received 50,000 RWF from JEAN CLAUDE. Your new balance: 52,300 RWF.", 1),
    ("Txld: 184592018. Wakohererejwe 25,000 RWF na UWAMARIYA. Amafaranga asigaye: 25,400 RWF.", 1),
    ("Transaction ID: 89345211. You have received 150,000 RWF from MUKASA PAUL. Your new account balance is 151,000 RWF.", 1),
    ("Trans ID: 09283746. Wakiriye 10,000 Frw avuye kwa NSHUTI. Reba balance kanda *182#", 1),
    ("Transfert reussi. Vous avez recu 30,000 RWF de la part de KAMALI. Solde: 34,000 RWF.", 1),
    ("Transaction ID: 6739201. Wahawe 200,000 RWF ya VUP. Kanda *182*1*1# wemeze uyihawe.", 1),

    # -- 2. Reversal / Mistake Scams (Emotional engineering) --
    ("Mbabarira nari nohereje amafaranga y'ishuri ry'umwana byibeshye kuri nimero yawe, kanda *182*4*1# wemeze bayansubize.", 1),
    ("Mwiriwe, namwe mumbabarire amafaranga 15,000 RWF nkoherereje yari ayo kugura imiti. Nyamuneka yansubize.", 1),
    ("Bite bro, bya 10K byaje byibeshye kuri number yawe, kanda *182* uyagarure.", 1),
    ("Muvandimwe, ayo mafaranga 45,000 nari nyohereje mubitaro kwishyura fagitire y'umurwayi, mbabarira uyansubize cyangwa ukande *182*4*1#", 1),
    ("Hello, I accidentally sent 25k meant for my mother's rent to your number. Please send it back, God bless you.", 1),
    ("Pardon, j'ai envoye 10,000 RWF par erreur sur ce numero. Pouvez-vous me les renvoyer svp? C'est urgent.", 1),
    ("Boss, amafaranga ya lisansi nyohereje byibeshye. Kanda *182*2*1*078XXXXXXX*5000# uyagarure bro.", 1),
    ("Nakoze ikosa nohereza 50,000 kuri iyi nimero, kanda *182*4*1# kugira ngo MTN iyansubize.", 1),

    # -- 3. Malicious USSD Codes (Tricking user to initiate transfer) --
    ("Kugira ngo wiyandikishe muri VUP, kanda *182*1*1*0788999999*50000# wemeze.", 1),
    ("MTN Promo: Kanda *182*8*1*078XXXXXXX*5000# kwakira inyongera ya 50,000 RWF.", 1),
    ("System Update: Dial *182*1*1*079XXXXXXX*20000# to prevent your MoMo account from being blocked.", 1),
    ("Kwakira inguzanyo ya MoKash ya 100,000 RWF, kanda *182*1*1*0782345678*10000# wemeze ubusabe.", 1),
    ("Pour debloquer votre compte, composez le *182*1*1*078XXXXXXX*5000# immediatement.", 1),
    ("MTN Reward: Win 5GB data and 10,000 RWF cash. Dial *182*1*1*0780000000*3000# to activate.", 1),
    ("Gufungura konti yawe ya MoMo yafunzwe, kanda *182*4*1*1#", 1),

    # -- 4. Phishing Links (KYC, Suspension, Prizes) --
    ("MTN INFO: Konti yawe ya MoMo igiye gufungwa kubera kutuzuza imyirondoro (KYC). Kanda hano: http://mtn-rw-update.com", 1),
    ("URGENT: Your MTN MoMo account is restricted. Verify your identity immediately at https://momo-verify-rw.xyz", 1),
    ("Cher client, votre compte MoMo sera suspendu. Mettez a jour vos informations: bit.ly/mtn-kyc-rw", 1),
    ("MTN REWARD: Watsindiye 1,000,000 RWF muri poromosiyo. Kanda hano uyabikuze: http://claim-momo.net", 1),
    ("Dear Customer, you have 1 pending MoMo transfer of 85,000 RWF. Confirm receipt here: https://mtn.momo-receive.com", 1),
    ("Kanda hano urebe amafaranga MTN yakugeneye uyu munsi: www.mtn-gifts.xyz", 1),
    ("Alerte Info: Verifiez votre numero NIN avec votre MoMo pour eviter la suspension de ligne: http://nida-mtn.verify.com", 1),
    ("You are the lucky winner of the MTN 25 Years Anniversary promo! Claim your cash prize: bit.ly/mtn-25-promo", 1),
    ("Irembo: Fagitire yawe ntiyishyuwe. Ishyure nonaha hano: http://irembo-pay-momo.xyz", 1),

    # -- 5. Impersonation (MTN Staff, Agents, Police) --
    ("Mwiriwe, ni kuri MTN Center. Twasanze konti yawe ifite ikibazo cy'umutekano. Oherereza PIN yawe kuri iyi nimero kugira ngo tuyikemure.", 1),
    ("Agent 10543: Your account is flagged for fraud. Call this number immediately to secure your funds.", 1),
    ("Tuguhamagaye ntiwitaba. Ohereza PIN yawe kugira ngo tuvugurure system ya MoMo yawe.", 1),
    ("RIB POLICE: Nimero yawe igiye gufungwa kubera gukoreshwa mu byaha. Vugana n'umukozi wacu kuri iyi nimero.", 1),
    ("Hello, this is MTN Customer Care. We detected unauthorized access to your MoMo. Reply with your PIN to block the hacker.", 1),
    ("Muraho, turi abakozi ba MTN. Twabonye hari umuntu ushaka kwinjira muri konti yawe. Kanda *182*4*1# wemeze ko ari wowe.", 1),
    ("Bonjour, ici le service client MTN. Veuillez confirmer votre code secret MoMo pour la mise a jour de votre puce.", 1),
    ("MoKash Agent: You qualify for a 500,000 RWF loan. Send a processing fee of 5,000 RWF to 078XXXXXXX to get it now.", 1),


    # ==========================================
    # 🟢 LEGITIMATE & ACTUAL TRANSACTIONS (Label = 0)
    # ==========================================

    # -- 1. P2P Transfers (Incoming & Outgoing) --
    ("Transaction ID: 178239401. You have received 15,000 RWF from JOHN MUGABO (25078XXXXXXX) on 13-Sep-2026 07:15:22. Your new balance: 17,400 RWF.", 0),
    ("Transaction ID: 178239455. You have transferred 5,000 RWF to ALICE UWASE (25078XXXXXXX) on 13-Sep-2026 08:10:00. Your new balance is 12,400 RWF. Fee paid: 150 RWF.", 0),
    ("Transaction ID: 298402910. Wakiriye 10,000 RWF yoherejwe na ERIC HABIMANA (25078XXXXXXX) kuwa 13-Sep-2026 09:00:05. Amafaranga asigaye: 10,200 RWF.", 0),
    ("Transaction ID: 483920192. Wohereje 2,500 RWF kuri CLAUDE NIYONZIMA (25079XXXXXXX) kuwa 13-Sep-2026 10:14:02. Amafaranga asigaye: 4,000 RWF. Ikiguzi: 50 RWF.", 0),
    ("Transaction ID: 902384751. Vous avez recu 50,000 RWF de DIANE MUKAMANA (25078XXXXXXX) le 13-Sep-2026 11:45:10. Nouveau solde: 155,000 RWF.", 0),
    ("Transaction ID: 583920183. You have transferred 100,000 RWF to PETER KAMALI (25078XXXXXXX) on 13-Sep-2026 12:30:45. Your new balance is 1,200 RWF. Fee paid: 1000 RWF.", 0),
    ("Transaction ID: 394857102. Wakiriye 3,000 RWF yoherejwe na MARIE CLAIRE (25079XXXXXXX) kuwa 13-Sep-2026 13:20:05. Amafaranga asigaye: 8,500 RWF.", 0),

    # -- 2. Merchant Payments (MoMoPay - Supermarkets, Motos, Pharmacies, Restos) --
    ("Transaction ID: 391028394. Payment of 2,500 RWF to CAFE KIGALI (123456) successful on 13-Sep-2026 12:30:15. Your new balance: 8,400 RWF.", 0),
    ("Transaction ID: 593029182. Wishyuye 15,000 RWF kuri SIMBA SUPERMARKET (654321) kuwa 13-Sep-2026 14:20:00. Amafaranga asigaye: 45,000 RWF.", 0),
    ("Transaction ID: 485920194. Payment of 1,200 RWF to YEGOMOTO (987654) successful on 13-Sep-2026 15:45:10. Your new balance: 3,200 RWF.", 0),
    ("Transaction ID: 293847561. Wishyuye 4,500 RWF kuri PHARMACIE CONSEIL (112233) kuwa 13-Sep-2026 16:10:05. Amafaranga asigaye: 12,000 RWF.", 0),
    ("Transaction ID: 584930291. Payment of 35,000 RWF to BRIOCHE (445566) successful on 13-Sep-2026 18:00:22. Your new balance: 10,000 RWF.", 0),
    ("Transaction ID: 748392019. Wishyuye 800 RWF kuri MOTO KIGALI (778899) kuwa 13-Sep-2026 19:30:00. Amafaranga asigaye: 5,600 RWF.", 0),

    # -- 3. Airtime, Bundles & Electricity (CASHPOWER) --
    ("Transaction ID: 102938475. You have successfully purchased 1,000 RWF airtime for 25078XXXXXXX on 13-Sep-2026 06:45:10. New balance: 11,400 RWF.", 0),
    ("Transaction ID: 948573920. Waguze bundle ya 1,000 RWF (1.5GB/24Hrs) kuri 25078XXXXXXX. Amafaranga asigaye: 2,400 RWF.", 0),
    ("Y'ello. You have successfully purchased Daily Pack 500 RWF (500MB + 15Min). Valid until 14-Sep-2026 23:59:59.", 0),
    ("Transaction ID: 394857102. You have successfully purchased electricity (CASHPOWER) for Meter 04321234567. Token: 1122 3344 5566 7788 9900. Units: 24.5 kWh. Amount: 5,000 RWF.", 0),
    ("Transaction ID: 293847561. Waguze umuriro wa CASHPOWER wa 2,000 RWF. Meter: 04112233445. Token: 4455 6677 8899 0011 2233. Amafaranga asigaye: 8,000 RWF.", 0),
    ("Y'ello. You have successfully purchased Weekly Pack 3000 RWF (3GB + 100Min). Valid until 20-Sep-2026 23:59:59.", 0),
    ("Transaction ID: 192837465. Waguze ikarita ya 500 RWF kuri 25079XXXXXXX. Amafaranga asigaye: 1,500 RWF.", 0),

    # -- 4. Cash In / Cash Out (Agents) --
    ("Transaction ID: 485920193. You have withdrawn 20,000 RWF from Agent MINEGA (019283) on 13-Sep-2026 10:15:00. New balance: 5,400 RWF. Fee: 300 RWF.", 0),
    ("Transaction ID: 758493021. You have deposited 50,000 RWF at Agent MINEGA (019283) on 13-Sep-2026 11:00:00. New balance: 55,400 RWF.", 0),
    ("Transaction ID: 293847102. Wabikuje 10,000 RWF kuri Agent UWIMANA (048392) kuwa 13-Sep-2026 12:45:10. Amafaranga asigaye: 12,000 RWF. Ikiguzi: 200 RWF.", 0),
    ("Transaction ID: 583920184. Washyizeho 100,000 RWF kuri Agent KABERA (092837) kuwa 13-Sep-2026 14:20:00. Amafaranga asigaye: 100,500 RWF.", 0),
    ("Transaction ID: 394857291. Vous avez retire 5,000 RWF chez l'Agent RUGAMBA (012345) le 13-Sep-2026 16:30:00. Nouveau solde: 2,400 RWF. Frais: 150 RWF.", 0),

    # -- 5. Bank to Wallet / Wallet to Bank (Push & Pull) --
    ("Transaction ID: 239485710. You have received 100,000 RWF from your BK Account (****1234) on 13-Sep-2026 13:00:00. Your new balance: 105,400 RWF.", 0),
    ("Transaction ID: 849302193. You have transferred 25,000 RWF to EQUITY BANK (****5678) on 13-Sep-2026. New balance: 80,400 RWF. Fee: 500 RWF.", 0),
    ("Transaction ID: 394857201. Wakiriye 50,000 RWF avuye kuri konti yawe ya BPR (****9012) kuwa 13-Sep-2026 14:15:00. Amafaranga asigaye: 55,000 RWF.", 0),
    ("Transaction ID: 485920195. Wohereje 20,000 RWF kuri konti ya I&M BANK (****3456) kuwa 13-Sep-2026 15:30:10. Amafaranga asigaye: 15,000 RWF. Ikiguzi: 300 RWF.", 0),
    ("Transaction ID: 593847562. Vous avez recu 200,000 RWF de votre compte ECOBANK (****7890) le 13-Sep-2026 17:00:05. Nouveau solde: 204,500 RWF.", 0),

    # -- 6. MoKash (Loans & Savings) --
    ("MoKash: Inguzanyo yawe ya 20,000 RWF yemejwe. Amafaranga ashyizwe kuri konti yawe ya MoMo. Ikiguzi: 1,800 RWF. Wishyure mbere ya 13-Oct-2026.", 0),
    ("MoKash: Wishyuye 10,000 RWF ku nguzanyo yawe. Ubusigane bw'inguzanyo ni 11,800 RWF.", 0),
    ("MoKash: Washyize 5,000 RWF kuri konti yawe yo kuzigama. Amafaranga azigamye yose hamwe ni 45,000 RWF.", 0),
    ("MoKash: Your loan request of 50,000 RWF has been approved. Your new MoMo balance is 54,000 RWF. Due date: 13-Oct-2026.", 0),
    ("MoKash: You have successfully repaid 54,500 RWF for your loan. Your outstanding loan balance is 0 RWF.", 0),
    ("MoKash: Your savings account has been credited with 150 RWF as monthly interest. Total savings: 35,150 RWF.", 0),

    # -- 7. Institutional, Irembo & Remittances --
    ("Transaction ID: 485920196. Payment of 15,000 RWF to IREMBO (Billing No: 987654321) successful on 13-Sep-2026 09:10:00. Your new balance: 10,000 RWF.", 0),
    ("Transaction ID: 593847291. Wishyuye 2,500 RWF kuri WASAC (Fagitire: 1234567) kuwa 13-Sep-2026 10:45:10. Amafaranga asigaye: 12,000 RWF.", 0),
    ("Transaction ID: 748392012. You have received a remittance of 50,000 RWF from WORLDREMIT. Your new MoMo balance is 52,000 RWF.", 0),
    ("Transaction ID: 859302194. Wakiriye 150,000 RWF avuye muri SENDWAVE. Amafaranga asigaye kuri MoMo: 155,500 RWF.", 0),
    ("Transaction ID: 394857291. You have successfully paid 10,000 RWF for RRA Taxes (TIN: 101234567). Your new balance is 4,500 RWF.", 0),
    ("Transaction ID: 102938475. Wakiriye 120,000 RWF yoherejwe na MINEDUC nk'umushahara. Amafaranga asigaye: 125,000 RWF.", 0),

    # -- 8. System & Security Alerts --
    ("MTN MoMo: Your PIN has been successfully changed on 13-Sep-2026 15:00:00. If you did not initiate this, call 100 immediately.", 0),
    ("Y'ello! Your MoMo account balance is 4,500 RWF. Thank you for using MTN.", 0),
    ("Urakoze gukoresha MTN MoMo. Umubare w'ibanga wawe wahinduwe neza.", 0),
    ("MTN Info: You have successfully linked your National ID to your MoMo account.", 0),
    ("MTN MoMo: Ubusabe bwawe bwo gukuraho amafaranga byabaye bihagaritswe. Hamagara 100 ufashwe.", 0)
]