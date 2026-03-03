import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class VipProvider extends ChangeNotifier {
  final ApiService _api = apiService;
  
  bool _isLoading = false;
  bool _isVip = false;
  DateTime? _vipExpireDate;
  int _keywordsCount = 1;
  List<dynamic> _products = [];
  String? _error;

  bool get isLoading => _isLoading;
  bool get isVip => _isVip;
  DateTime? get vipExpireDate => _vipExpireDate;
  int get keywordsCount => _keywordsCount;
  List<dynamic> get products => _products;
  String? get error => _error;

  VipProvider() {
    loadVipStatus();
    loadProducts();
  }

  Future<void> loadVipStatus() async {
    try {
      final response = await _api.getVipStatus();
      if (response.statusCode == 200) {
        _isVip = response.data['is_vip'] ?? false;
        _keywordsCount = response.data['keywords_count'] ?? 1;
        
        final expireDate = response.data['vip_expire_date'];
        if (expireDate != null) {
          _vipExpireDate = DateTime.parse(expireDate);
        }
        
        notifyListeners();
      }
    } catch (e) {
      _error = '加载VIP状态失败';
    }
  }

  Future<void> loadProducts() async {
    try {
      final response = await _api.getVipProducts();
      if (response.statusCode == 200) {
        _products = response.data['products'] ?? [];
        notifyListeners();
      }
    } catch (e) {
      // 加载产品失败
    }
  }

  /// 创建支付宝当面付订单
  Future<Map<String, dynamic>?> createOrder(int durationDays) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _api.createPayOrder(durationDays);
      
      _isLoading = false;
      notifyListeners();
      
      if (response.statusCode == 200) {
        return response.data;
      }
    } catch (e) {
      _error = '创建订单失败';
    }

    _isLoading = false;
    notifyListeners();
    return null;
  }

  /// 检查支付状态
  Future<bool> checkPayment(String orderNo) async {
    try {
      final response = await _api.checkPayment(orderNo);
      if (response.statusCode == 200) {
        if (response.data['status'] == 'paid') {
          await loadVipStatus();
          return true;
        }
      }
    } catch (e) {
      // 检查失败
    }
    return false;
  }

  /// 取消订单
  Future<bool> cancelOrder(String orderNo) async {
    try {
      final response = await _api.cancelOrder(orderNo);
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
