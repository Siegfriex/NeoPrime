const fs = require('fs-extra');
const path = require('path');

const pptDir = path.resolve(__dirname, '../../../ppt');
const distDir = path.resolve(__dirname, '../dist/ir-deck');

console.log('📊 Copying IR Deck...');
console.log(`   From: ${pptDir}`);
console.log(`   To:   ${distDir}`);

fs.copySync(pptDir, distDir, {
  filter: (src) => {
    const basename = path.basename(src);
    // 제외 목록
    if (basename === 'package.json' || basename === 'package-lock.json') return false;
    if (basename === 'vite.config.js') return false;
    if (basename === 'generate-pdf.js' || basename === 'generate-pdf.cjs') return false;
    if (basename.endsWith('.pdf')) return false;
    return true;
  }
});

console.log('✅ Done: dist/ir-deck/');
