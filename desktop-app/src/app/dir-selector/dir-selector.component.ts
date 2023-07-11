import { Component, ChangeDetectorRef } from '@angular/core';
import { ViewChild } from '@angular/core';
import { MatTable } from '@angular/material/table';

declare var window: any;

@Component({
  selector: 'app-dir-selector',
  templateUrl: './dir-selector.component.html',
  styleUrls: ['./dir-selector.component.css'],
})
export class DirSelectorComponent {
  files: any[] = [];
  models: string[] = [
    'text-embedding-ada-002',
    'google/bert_uncased_L-12_H-768_A-12',
    'all-MiniLM-L6-v2',
    'allenai/scibert_scivocab_uncased',
    'emilyalsentzer/Bio_ClinicalBERT',
  ];
  strategies: string[] = ['l2', 'cosine', 'ip'];

  selectedModel = '';
  selectedStrategy = '';

  query = '';
  selectedSource = '';
  selectedPath: string = '';

  benchmarkDisabled = false;

  displayedColumns: string[] = [
    'Embedding Model',
    'DB Type',
    'Strategy',
    'Average k',
    'Sigma',
    'Frequency',
    'Queries',
  ];

  // To hold the queries and sources
  lines: { query: string; source: string }[] = [{ query: '', source: '' }];

  addLine() {
    this.lines.push({ query: '', source: '' });
  }

  removeLine(index: number) {
    this.lines.splice(index, 1);
  }

  dataSource: any[] = [
    {
      'Embedding Model': 'TEST_ROW',
      'DB Type': 'Test',
      Strategy: 'test',
      'Average k': 4,
      Sigma: 1,
      Frequency: 3,
      Queries: 1,
    },
  ];

  @ViewChild(MatTable) table!: MatTable<any>;

  constructor(private cdr: ChangeDetectorRef) {}

  openDirectory() {
    window.electron.openDirectory();
  }

  displayFiles() {
    window.electron.displayFiles(this.selectedPath);
  }

  startBenchmark() {
    new window.Notification('Bencmark Started', {
      body: `Path: "${this.selectedPath}"
      Source: "${this.selectedSource}"
      Model: "${this.selectedModel}"
      Strategy: "${this.selectedStrategy}"
      Query: "${this.query}"
      `,
    });
    window.electron.startBenchmark(
      this.selectedModel,
      this.selectedStrategy,
      this.query,
      this.selectedPath,
      this.selectedSource,
      this.lines
    );
    this.benchmarkDisabled = true;
  }

  generateQuery(i: number) {
    let source = this.lines[i].source;
    let path = this.selectedPath;
    window.electron.generateQuery(source, path);
    console.log('PPPAATTHHH', source, path);
  }

  ngOnInit() {
    window.electron.onDirectorySelected((path: any) => {
      this.selectedPath = path;
      this.cdr.detectChanges();
      this.displayFiles();
    });

    window.electron.onDirectoryFiles((content: any) => {
      this.files = content;
      this.cdr.detectChanges();
    });

    window.electron.onBenchmarkData((message: any) => {
      this.benchmarkDisabled = !this.benchmarkDisabled;
      let data = JSON.parse(message);
      console.log(data[0]);
      this.dataSource.push(data[0]);
      this.cdr.detectChanges();
      console.log(this.dataSource);
      new window.Notification('Benchmark Finished', {
        body: `Benchmark results can now be seen in the app. `,
      });
      this.table.renderRows();
      this.cdr.detectChanges();
    });
  }

  ngOnDestroy() {
    window.electron.removeDirectorySelectedListener();
    window.electron.removeDirectoryFilesListener();
    window.electron.removeBenchmarkDataListener();
  }
}
