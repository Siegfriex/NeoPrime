const puppeteer = require('puppeteer');
const path = require('path');

async function generatePDF(htmlPath, outputPath) {
    const browser = await puppeteer.launch({
        headless: 'new'
    });
    const page = await browser.newPage();
    
    // 파일 URL로 변환
    const fileUrl = `file:///${htmlPath.replace(/\\/g, '/')}`;
    console.log(`Loading: ${fileUrl}`);
    
    await page.goto(fileUrl, { 
        waitUntil: 'networkidle0',
        timeout: 60000 
    });
    
    // PDF 생성 (A4 가로 모드, 프레젠테이션에 적합)
    await page.pdf({
        path: outputPath,
        format: 'A4',
        landscape: true,
        printBackground: true,
        margin: { top: '0', right: '0', bottom: '0', left: '0' }
    });
    
    console.log(`PDF saved: ${outputPath}`);
    await browser.close();
}

// DesignMate PDF 생성
const designmatePath = path.resolve(__dirname, 'designmate', 'index.html');
const designmateOutput = path.resolve(__dirname, 'designmate', 'DesignMate_IR_Deck.pdf');

generatePDF(designmatePath, designmateOutput)
    .then(() => console.log('Done!'))
    .catch(err => console.error('Error:', err));
