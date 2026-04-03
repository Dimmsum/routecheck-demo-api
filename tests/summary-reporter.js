class SummaryReporter {
  constructor() {
    this.passed = 0;
    this.failed = 0;
    this.skipped = 0;
    this.failures = [];
  }

  onTestEnd(test, result) {
    if (result.status === 'passed') {
      this.passed++;
    } else if (result.status === 'failed' || result.status === 'timedOut') {
      this.failed++;
      this.failures.push({
        title: test.title,
        error: result.error?.message || 'Unknown error',
      });
    } else if (result.status === 'skipped') {
      this.skipped++;
    }
  }

  onEnd() {
    const total = this.passed + this.failed + this.skipped;
    const line = '─'.repeat(50);
    console.log('\n' + line);
    console.log('  TEST SUMMARY');
    console.log(line);
    console.log(`  Total:   ${total}`);
    console.log(`  Passed:  ${this.passed}  ✓`);
    console.log(`  Failed:  ${this.failed}${this.failed > 0 ? '  ✗' : ''}`);
    if (this.skipped > 0) console.log(`  Skipped: ${this.skipped}`);
    console.log(line);

    if (this.failures.length > 0) {
      console.log('\n  FAILED TESTS:');
      this.failures.forEach((f, i) => {
        console.log(`\n  ${i + 1}. ${f.title}`);
        console.log(`     ${f.error.split('\n')[0]}`);
      });
      console.log('');
    }
  }
}

module.exports = SummaryReporter;
