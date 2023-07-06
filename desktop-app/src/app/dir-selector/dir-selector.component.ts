import { Component, ChangeDetectorRef } from '@angular/core';

declare var window: any;

@Component({
  selector: 'app-dir-selector',
  templateUrl: './dir-selector.component.html',
  styleUrls: ['./dir-selector.component.css'],
})
export class DirSelectorComponent {
  selectedPath: string = '';
  files: any[] = [];
  models: string[] = [
    'text-embedding-ada-002',
    'bert_uncased_L-12_H-768_A-12',
    'all-MiniLM-L6-v2',
    'scibert_scivocab_uncased',
    'Bio_ClinicalBERT',
  ];
  strategies: string[] = ['l2', 'cosine', 'ip'];
  selectedModel = '';
  selectedStrategy = '';
  selectedSource = '';
  query = '';

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
      Model: "${this.selectedModel}"
      Strategy: "${this.selectedStrategy}"
      Query: "${this.query}"
      `,
    });
    window.electron.startBenchmark(
      this.selectedModel,
      this.selectedStrategy,
      this.query,
      this.selectedPath
    );
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
  }

  ngOnDestroy() {
    window.electron.removeDirectorySelectedListener();
    window.electron.removeDirectoryFilesListener();
  }
}
