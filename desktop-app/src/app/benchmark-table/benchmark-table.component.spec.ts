import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BenchmarkTableComponent } from './benchmark-table.component';

describe('BenchmarkTableComponent', () => {
  let component: BenchmarkTableComponent;
  let fixture: ComponentFixture<BenchmarkTableComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [BenchmarkTableComponent]
    });
    fixture = TestBed.createComponent(BenchmarkTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
