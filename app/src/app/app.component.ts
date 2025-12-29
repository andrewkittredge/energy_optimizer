import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

interface OptimizeBody {
  [key: string]: number | Record<string, number>;
}

interface OptimizeResponse {
  solar_capacity: number;
  battery_capacity: number;
  off_peak_grid_usage: number;
  peak_grid_consumption: number;
}

interface OptimizeParams {
  peak_price: number;
  off_peak_price: number;
  battery_cost_per_kw: number;
  peak_consumption: number;
  off_peak_consumption: number;
  solar_installation_sizes: Record<string, number>;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  title = 'energy-optimizer';
  
  // Form values
  peakPrice!: number;
  offPeakPrice!: number;
  batteryCostPerKw!: number;
  peakConsumption!: number;
  offPeakConsumption!: number;
  solarInstallationSizes!: string;
  
  result: OptimizeResponse | null = null;
  resultError: string = '';
  isRunning: boolean = false;

  constructor(private route: ActivatedRoute, private router: Router) {}

  ngOnInit(): void {
    this.loadFormDefaults();
    this.loadStateFromUrl();
  }

  loadFormDefaults(): void {
    fetch('http://localhost:8000/defaults')
      .then((resp) => resp.json())
      .then((defaults: OptimizeParams) => {
        this.peakPrice = defaults.peak_price;
        this.offPeakPrice = defaults.off_peak_price;
        this.batteryCostPerKw = defaults.battery_cost_per_kw;
        this.peakConsumption = defaults.peak_consumption;
        this.offPeakConsumption = defaults.off_peak_consumption;
        this.solarInstallationSizes = JSON.stringify(defaults.solar_installation_sizes);
      })
      .catch((err) => {
        console.warn('Failed to load defaults from API:', err);
      });
  }

  loadStateFromUrl(): void {
    this.route.queryParams.subscribe((params) => {
      if (params['peakPrice'] !== undefined) this.peakPrice = Number(params['peakPrice']);
      if (params['offPeakPrice'] !== undefined) this.offPeakPrice = Number(params['offPeakPrice']);
      if (params['batteryCostPerKw'] !== undefined) this.batteryCostPerKw = Number(params['batteryCostPerKw']);
      if (params['peakConsumption'] !== undefined) this.peakConsumption = Number(params['peakConsumption']);
      if (params['offPeakConsumption'] !== undefined) this.offPeakConsumption = Number(params['offPeakConsumption']);
      if (params['solarInstallationSizes'] !== undefined) {
        let raw = params['solarInstallationSizes'];
        try {
          // If it's URL-encoded JSON, decode first
          const decoded = decodeURIComponent(String(raw));
          // If decoded looks like JSON, use it; otherwise try raw
          const candidate = decoded.trim().startsWith('{') ? decoded : String(raw);
          // Normalize to a pretty JSON string for the textarea
          const parsed = JSON.parse(candidate);
          this.solarInstallationSizes = JSON.stringify(parsed);
        } catch (e) {
          // fallback: set raw string (e.g., already a compact JSON or simple string)
          this.solarInstallationSizes = String(raw);
        }
      }
    });
  }

  updateUrlState(): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        peakPrice: this.peakPrice,
        offPeakPrice: this.offPeakPrice,
        batteryCostPerKw: this.batteryCostPerKw,
        peakConsumption: this.peakConsumption,
        offPeakConsumption: this.offPeakConsumption,
        solarInstallationSizes: this.solarInstallationSizes,
      },
      queryParamsHandling: 'merge',
    });
  }

  async onSubmit(): Promise<void> {
    const body: OptimizeBody = {
      peak_price: this.peakPrice,
      off_peak_price: this.offPeakPrice,
      battery_cost_per_kw: this.batteryCostPerKw,
      peak_consumption: this.peakConsumption,
      off_peak_consumption: this.offPeakConsumption,
    };

    try {
      body['solar_installation_sizes'] = JSON.parse(this.solarInstallationSizes);
    } catch (err) {
      this.resultError = 'Invalid JSON for solar sizes';
      return;
    }

    this.result = null;
    this.resultError = '';
    this.isRunning = true;

    try {
      const resp = await fetch('http://localhost:8000/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const j = (await resp.json()) as OptimizeResponse;
      this.result = j;
      this.updateUrlState();
    } catch (err) {
      this.resultError = 'Request failed: ' + (err instanceof Error ? err.message : String(err));
    } finally {
      this.isRunning = false;
    }
  }
}
