import {
  Component,
  ChangeDetectorRef,
  Input,
  Output,
  EventEmitter,
} from '@angular/core';
import { ViewChild } from '@angular/core';
import { MatTable } from '@angular/material/table';
import { BenchmarkDisabledService } from '../benchmark-disabled.service';

declare var window: any;

@Component({
  selector: 'app-dir-selector',
  templateUrl: './dir-selector.component.html',
  styleUrls: ['./dir-selector.component.css'],
})
export class DirSelectorComponent {
  files: any[] = [];
  models: string[] = [
    // 'text-embedding-ada-002',
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
  queryDisabled = false;

  // To hold the queries and sources
  lines: { query: string; source: string }[] = [{ query: '', source: '' }];

  addLine() {
    this.lines.push({ query: '', source: '' });
  }

  removeLine(index: number) {
    this.lines.splice(index, 1);
  }

  @ViewChild(MatTable) table!: MatTable<any>;

  constructor(
    private cdr: ChangeDetectorRef,
    private benchmarkDisabledService: BenchmarkDisabledService
  ) {
    this.benchmarkDisabledService.benchmarkDisabled$.subscribe(
      (status: boolean) => {
        this.benchmarkDisabled = status;
        this.cdr.detectChanges()
      }
    );
  }

  changeBenchmarkDisableStatus() {
    
  }
  openDirectory() {
    window.electron.openDirectory();
  }

  displayFiles() {
    window.electron.displayFiles(this.selectedPath);
  }

  startBenchmark() {
    new window.Notification('Benchmark Started', {
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
    this.benchmarkDisabledService.setBenchmarkDisabled(true);
    this.cdr.detectChanges();
    console.log('HELLO', this.benchmarkDisabled);
  }

  generateQuery(index: number) {
    let source = this.lines[index].source;
    let path = this.selectedPath;
    window.electron.generateQuery(path, source, index);
    this.queryDisabled = true;
    console.log('PPPAATTHHH', source, path, index);
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

    window.electron.onQuery((message: any) => {
      let array = JSON.parse(message);
      let query = array[0];
      let index = array[1];
      this.lines[index].query = query;
      this.queryDisabled = !this.queryDisabled;
      this.cdr.detectChanges();
    });
  }

  ngOnDestroy() {
    window.electron.removeDirectorySelectedListener();
    window.electron.removeDirectoryFilesListener();
    window.electron.removeBenchmarkDataListener();
  }
}
