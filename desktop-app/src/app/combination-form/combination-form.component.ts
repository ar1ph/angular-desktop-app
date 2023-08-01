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
  selector: 'app-combination-form',
  templateUrl: './combination-form.component.html',
  styleUrls: ['./combination-form.component.css'],
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


  selectedPath: string = '';

  benchmarkDisabled = false;
  queryDisabled = false;

  // To hold the queries and sources
  lines: { query: string; source: string; queryDisabled: boolean }[] = [
    { query: '', source: '', queryDisabled: false },
  ];

  addLine() {
    this.lines.push({ query: '', source: '', queryDisabled: false });
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
        this.cdr.detectChanges();
      }
    );
  }

  formIsEmpty() {
    return (
      this.selectedModel == '' ||
      this.selectedStrategy == '' ||
      this.lines.some((line) => line.query == '' || line.source == '')
    );
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
      Model: "${this.selectedModel}"
      Strategy: "${this.selectedStrategy}"   `,
    });
    window.electron.startBenchmark(
      this.selectedModel,
      this.selectedStrategy,
      this.selectedPath,
      this.lines
    );
    this.benchmarkDisabledService.setBenchmarkDisabled(true);
    this.cdr.detectChanges();
    console.log('DISABLED TEST', this.benchmarkDisabled);
  }

  //Send filepath to python script to generate query
  generateQuery(index: number) {
    let source = this.lines[index].source;
    let path = this.selectedPath;
    window.electron.generateQuery(path, source, index);
    this.lines[index].queryDisabled = true;
    console.log('PATH', source, path, index);
  }

  ngOnInit() {
    //Directory is selected
    window.electron.onDirectorySelected((path: any) => {
      this.selectedPath = path;
      this.cdr.detectChanges();
      this.displayFiles();
    });

    //Receiving files in directory
    window.electron.onDirectoryFiles((content: any) => {
      this.files = content;
      this.cdr.detectChanges();
    });

    //Receiving query
    window.electron.onQuery((message: any) => {
      let array = JSON.parse(message);
      let query = array[0];
      let index = array[1];
      this.lines[index].query = query;
      this.lines[index].queryDisabled = false;
      this.cdr.detectChanges();
    });
  }

  ngOnDestroy() {
    window.electron.removeDirectorySelectedListener();
    window.electron.removeDirectoryFilesListener();
    window.electron.removeBenchmarkDataListener();
  }
}
