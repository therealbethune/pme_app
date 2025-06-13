#!/usr/bin/env node

import { execSync } from 'child_process';
import { existsSync, readFileSync } from 'fs';
import { join } from 'path';

interface TestResult {
  name: string;
  passed: boolean;
  message: string;
}

class FrontendCleanupTester {
  private results: TestResult[] = [];

  test(name: string, condition: boolean, message: string): void {
    this.results.push({
      name,
      passed: condition,
      message: condition ? `✅ ${message}` : `❌ ${message}`
    });
  }

  async runTests(): Promise<void> {
    console.log('🧪 Running frontend cleanup and API configuration tests...\n');

    // Test 1: Check node_modules is removed
    const nodeModulesPath = join(process.cwd(), 'pme_calculator/frontend/node_modules');
    this.test(
      'node_modules cleanup',
      !existsSync(nodeModulesPath),
      'node_modules directory should not exist in repository'
    );

    // Test 2: Check dist is removed
    const distPath = join(process.cwd(), 'pme_calculator/frontend/dist');
    this.test(
      'dist cleanup',
      !existsSync(distPath),
      'dist directory should not exist in repository'
    );

    // Test 3: Check .gitignore contains proper entries
    const gitignorePath = join(process.cwd(), '.gitignore');
    if (existsSync(gitignorePath)) {
      const gitignoreContent = readFileSync(gitignorePath, 'utf-8');
      this.test(
        'gitignore node_modules',
        gitignoreContent.includes('node_modules'),
        'node_modules should be in .gitignore'
      );
      this.test(
        'gitignore dist',
        gitignoreContent.includes('dist'),
        'dist should be in .gitignore'
      );
    } else {
      this.test('gitignore exists', false, '.gitignore file should exist');
    }

    // Test 4: Check for hardcoded port 3000 references
    try {
      const grepResult = execSync(
        'grep -r ":3000" pme_calculator/frontend/ --include="*.js" --include="*.ts" --include="*.html" || true',
        { encoding: 'utf-8' }
      );
      this.test(
        'no hardcoded port 3000',
        grepResult.trim() === '',
        'Should not contain hardcoded port 3000 references'
      );
    } catch (error) {
      this.test('port 3000 check', false, 'Error checking for port 3000 references');
    }

    // Test 5: Check API_BASE environment variable support
    const configFiles = [
      'pme_calculator/frontend/src/config/api.ts',
      'pme_calculator/frontend/src/services/api.ts',
      'pme_calculator/frontend/src/services/analysisService.ts'
    ];

    for (const file of configFiles) {
      const filePath = join(process.cwd(), file);
      if (existsSync(filePath)) {
        const content = readFileSync(filePath, 'utf-8');
        this.test(
          `${file} env support`,
          content.includes('VITE_API_BASE') || content.includes('import.meta.env'),
          `${file} should support environment variables`
        );
      }
    }

    // Test 6: Check vite.config.ts has proper env configuration
    const viteConfigPath = join(process.cwd(), 'pme_calculator/frontend/vite.config.ts');
    if (existsSync(viteConfigPath)) {
      const viteConfig = readFileSync(viteConfigPath, 'utf-8');
      this.test(
        'vite config env support',
        viteConfig.includes('envPrefix') || viteConfig.includes('VITE_'),
        'vite.config.ts should support VITE_ environment variables'
      );
    }

    // Print results
    console.log('\n📊 Test Results:');
    console.log('================');
    
    let passed = 0;
    for (const result of this.results) {
      console.log(result.message);
      if (result.passed) passed++;
    }

    console.log(`\n🎯 Summary: ${passed}/${this.results.length} tests passed`);
    
    if (passed === this.results.length) {
      console.log('🎉 All tests passed! Frontend cleanup and API configuration complete.');
    } else {
      console.log('❌ Some tests failed. Please review the issues above.');
      process.exit(1);
    }
  }
}

// Run the tests
const tester = new FrontendCleanupTester();
tester.runTests().catch(console.error); 