import { TestBed } from '@angular/core/testing';

import { BenchmarkDisabledService } from './benchmark-disabled.service';

describe('BenchmarkDisabledService', () => {
  let service: BenchmarkDisabledService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BenchmarkDisabledService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
