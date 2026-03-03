import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class TrendingProvider extends ChangeNotifier {
  final ApiService _api = apiService;
  
  bool _isLoading = false;
  List<dynamic> _trendingData = [];
  List<dynamic> _platforms = [];
  String? _selectedPlatform;
  String? _error;

  bool get isLoading => _isLoading;
  List<dynamic> get trendingData => _trendingData;
  List<dynamic> get platforms => _platforms;
  String? get selectedPlatform => _selectedPlatform;
  String? get error => _error;

  TrendingProvider() {
    loadPlatforms();
  }

  Future<void> loadPlatforms() async {
    try {
      final response = await _api.getPlatforms();
      if (response.statusCode == 200) {
        _platforms = response.data['platforms'] ?? [];
        notifyListeners();
      }
    } catch (e) {
      _error = '加载平台列表失败';
    }
  }

  Future<void> loadTrending({String? platform, String? keywords}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.getTrending(
        platform: platform ?? _selectedPlatform,
        keywords: keywords,
      );
      
      if (response.statusCode == 200) {
        _trendingData = response.data ?? [];
      }
    } catch (e) {
      _error = '加载热点数据失败';
    }

    _isLoading = false;
    notifyListeners();
  }

  void selectPlatform(String? platform) {
    _selectedPlatform = platform;
    loadTrending(platform: platform);
  }

  Future<void> refresh() async {
    await loadTrending();
  }
}
