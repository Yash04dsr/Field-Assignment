function createCleanBilingualSurvey() {
    var form = FormApp.create('Sunder Nursery Visitor Survey');
    
    form.setProgressBar(true);
    form.setCollectEmail(false);
    
    var description = "Hello! 🌸 We are students from IIT Delhi conducting a quick academic study to understand the true value of Sunder Nursery. It will only take 2 minutes, and your responses are completely anonymous.\n\n" +
                      "नमस्ते! 🌸 हम IIT दिल्ली के छात्र हैं और सुंदर नर्सरी के महत्व को समझने के लिए एक अध्ययन कर रहे हैं। इसमें केवल 2 मिनट लगेंगे, और आपकी प्रतिक्रियाएँ पूरी तरह से अनाम रहेंगी।";
    form.setDescription(description);
  
    // ==========================================
    // PAGE 1: CONSERVATION & HERITAGE (CVM Core)
    // ==========================================
    
    form.addCheckboxItem()
        .setTitle('What aspects of Sunder Nursery do you value the most? \n(आप सुंदर नर्सरी के किन पहलुओं को सबसे अधिक महत्व देते हैं?)')
        .setChoiceValues([
          'Aesthetic and scenic beauty | सौंदर्य और प्राकृतिक सुंदरता',
          'Quietude and escape from the city | शांति और शहर की भीड़ से दूर',
          'Protection of 16th-century monuments | 16वीं सदी के स्मारकों का संरक्षण',
          'Protection of native plants and birds | देशी पौधों और पक्षियों का संरक्षण',
          'Availability for future generations | भावी पीढ़ियों के लिए उपलब्धता'
        ])
        .setRequired(true);
  
    var willingnessItem = form.addMultipleChoiceItem()
        .setTitle('Sunder Nursery is a 90-acre heritage park. Would you be willing to pay a slightly higher entry fee to guarantee the permanent protection of the park\'s monuments, gardens, and birds? \n(क्या आप पार्क की स्थायी सुरक्षा सुनिश्चित करने के लिए थोड़ा अधिक प्रवेश शुल्क देने को तैयार होंगे?)')
        .setRequired(true);
  
    // ==========================================
    // PAGE 2: AMOUNT (Only shown if they say YES)
    // ==========================================
    var amountPage = form.addPageBreakItem().setTitle('Contribution Details | योगदान विवरण');
    
    form.addMultipleChoiceItem()
        .setTitle('What is the MAXIMUM extra amount you would be willing to pay per visit? \n(प्रति विजिट आप अधिकतम कितनी अतिरिक्त राशि देने को तैयार होंगे?)')
        .setChoiceValues([
          '₹10 extra | ₹10 अतिरिक्त', 
          '₹20 extra | ₹20 अतिरिक्त', 
          '₹50 extra | ₹50 अतिरिक्त', 
          '₹100 extra | ₹100 अतिरिक्त'
        ])
        .setRequired(true);
  
    // ==========================================
    // PAGE 3: REASON (Only shown if they say NO)
    // ==========================================
    var reasonPage = form.addPageBreakItem().setTitle('Feedback | प्रतिक्रिया');
    
    form.addMultipleChoiceItem()
        .setTitle('Since you chose NOT to pay extra, what is your main reason? \n(चूँकि आपने अतिरिक्त भुगतान नहीं करने का विकल्प चुना है, तो इसका मुख्य कारण क्या है?)')
        .setChoiceValues([
          'I cannot afford to pay more | मैं और अधिक भुगतान नहीं कर सकता', 
          'The government/management should pay, not visitors | सरकार/प्रबंधन को खर्च उठाना चाहिए, आगंतुकों को नहीं', 
          'I do not think the park is worth paying more for | मुझे नहीं लगता कि इसके लिए अधिक भुगतान करना उचित है'
        ])
        .setRequired(true);
  
    // ==========================================
    // PAGE 4: FUTURE GENERATIONS (Non-Use Value)
    // ==========================================
    var futurePage = form.addPageBreakItem().setTitle('🌱 Section 2: Future Generations | भावी पीढ़ियों के लिए');
    
    form.addMultipleChoiceItem()
        .setTitle('How important is it to you that Sunder Nursery is preserved for future generations? \n(आपके लिए यह कितना महत्वपूर्ण है कि सुंदर नर्सरी को भावी पीढ़ियों के लिए संरक्षित किया जाए?)')
        .setChoiceValues([
          'Very important | बहुत ज़रूरी', 
          'Somewhat important | कुछ हद तक ज़रूरी', 
          'Not important | ज़रूरी नहीं'
        ])
        .setRequired(true);
  
    form.addMultipleChoiceItem()
        .setTitle('Would you support the conservation of this park even if you could never visit it again? \n(क्या आप इस पार्क के संरक्षण का समर्थन करेंगे, भले ही आप यहां दोबारा कभी न आ सकें?)')
        .setChoiceValues([
          'Yes | हाँ', 
          'No | नहीं'
        ])
        .setRequired(true);
  
    // ==========================================
    // UX IMPROVEMENT: APPLY SKIP LOGIC
    // ==========================================
    willingnessItem.setChoices([
      willingnessItem.createChoice('Yes | हाँ', amountPage),
      willingnessItem.createChoice('No | नहीं', reasonPage)
    ]);
    amountPage.setGoToPage(futurePage);
    reasonPage.setGoToPage(futurePage);
  
    // ==========================================
    // PAGE 5: TRAVEL (TCM Core)
    // ==========================================
    form.addPageBreakItem().setTitle('🚗 Section 3: Travel & Accessibility | यात्रा और पहुंच');
  
    form.addTextItem()
        .setTitle('Which neighborhood, locality, or PIN code did you travel from today? \n(आज आप किस इलाके या पिन कोड से यहाँ आए हैं?)')
        .setRequired(true);
  
    form.addMultipleChoiceItem()
        .setTitle('What was your primary mode of transport today? \n(आज आपका यातायात का मुख्य साधन क्या था?)')
        .setChoiceValues([
          'Walked | पैदल', 
          'Metro or Bus | मेट्रो या बस', 
          'Auto, Taxi, or Cab | ऑटो, टैक्सी या कैब', 
          'Personal Car or Bike | अपनी कार या बाइक'
        ])
        .setRequired(true);
  
    form.addMultipleChoiceItem()
        .setTitle('Is Sunder Nursery the ONLY place you traveled to visit on this trip? \n(क्या इस यात्रा में आप केवल सुंदर नर्सरी देखने आए हैं?)')
        .setChoiceValues([
          'Yes, it is my only destination | हाँ, यह मेरा एकमात्र गंतव्य है', 
          'No, I am also visiting nearby places | नहीं, मैं आसपास के अन्य स्थान भी देख रहा हूँ'
        ])
        .setRequired(true);
  
    form.addMultipleChoiceItem()
        .setTitle('What is your estimated one-way travel cost to reach here? \n(यहाँ पहुँचने का आपका अनुमानित एक तरफ़ा यात्रा खर्च क्या है?)')
        .setChoiceValues([
          '₹0–₹20', 
          '₹21–₹50', 
          '₹51–₹100', 
          '₹101–₹200', 
          'More than ₹200 | ₹200 से ज़्यादा'
        ])
        .setRequired(true);
  
    form.addMultipleChoiceItem()
        .setTitle('How much time did it take you to reach the park today (one way)? \n(आज आपको पार्क तक पहुँचने में कितना समय लगा?)')
        .setChoiceValues([
          'Less than 15 min | 15 मिनट से कम', 
          '15–30 min | 15–30 मिनट', 
          '31–60 min | 31–60 मिनट', 
          'More than 1 hour | 1 घंटे से ज़्यादा'
        ])
        .setRequired(true);
  
    // ==========================================
    // PAGE 6: DEMOGRAPHICS 
    // ==========================================
    form.addPageBreakItem().setTitle('📍 Section 4: About You | आपके बारे में');
    
    form.addMultipleChoiceItem()
        .setTitle('How often do you visit Sunder Nursery? \n(आप सुंदर नर्सरी कितनी बार आते हैं?)')
        .setChoiceValues([
          'First time | पहली बार', 
          '1–3 times a month | महीने में 1-3 बार', 
          'Weekly or more | हफ्ते में एक बार या ज़्यादा', 
          'Rarely | शायद ही कभी'
        ])
        .setRequired(true);
  
    form.addMultipleChoiceItem()
        .setTitle('Your age group \n(आपकी आयु वर्ग)')
        .setChoiceValues([
          'Under 18', 
          '18–35', 
          '36–60', 
          '60+'
        ])
        .setRequired(true);
  
    form.addMultipleChoiceItem()
        .setTitle('Your occupation & approximate monthly income \n(आपका पेशा और अनुमानित मासिक आय)')
        .setChoiceValues([
          'Student | विद्यार्थी', 
          'Under ₹50,000 | ₹50,000 से कम', 
          '₹50,000–₹1,00,000', 
          'Above ₹1,00,000 | ₹1,00,000 से ज़्यादा'
        ])
        .setRequired(true);
  
    // ==========================================
    // CUSTOM THANK YOU MESSAGE
    // ==========================================
    var thankYouMessage = "Thank you so much for your time! Your responses are incredibly valuable to our IIT Delhi research project. Have a wonderful day at Sunder Nursery! 🌸\n\n" +
                          "अपना बहुमूल्य समय देने के लिए बहुत-बहुत धन्यवाद! आपकी प्रतिक्रियाएँ हमारे IIT दिल्ली के शोध प्रोजेक्ट के लिए अत्यंत महत्वपूर्ण हैं। सुंदर नर्सरी में आपका दिन शुभ हो! 🌸";
    form.setConfirmationMessage(thankYouMessage);
  
    Logger.log('Form URL: ' + form.getEditUrl());
  }